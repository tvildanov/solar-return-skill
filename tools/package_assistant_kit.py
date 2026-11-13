#!/usr/bin/env python3
"""Build a shareable kit: standalone conversation adapters + native skill ZIP.

This is a download bundle, not a universal installer. No code is executed.
"""
import argparse
import hashlib
import io
from pathlib import Path
import zipfile

from package_skill import ROOT, build_bytes

ADAPTERS = ("README.md", "claude.md", "chatgpt.md", "grok.md", "gemini.md", "any-agent.md")


def adapter_bytes(name):
    source = ROOT / "adapters" / name
    if source.is_symlink() or source.parent.is_symlink():
        raise ValueError(f"Refusing symlink adapter: {name}")
    return source.read_bytes()


def expected_files():
    files = {"README-FIRST.md": adapter_bytes("README.md"),
             "LICENSE": (ROOT / "LICENSE").read_bytes(),
             "solar-return.zip": build_bytes()}
    for name in ADAPTERS[1:]:
        files[name] = adapter_bytes(name)
    return files


def archive_bytes(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo("solar-return-assistant-kit/" + name, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = archive_bytes(expected_files())
    archive = ROOT / "solar-return-assistant-kit.zip"
    checksum = ROOT / "solar-return-assistant-kit.zip.sha256"
    line = f"{hashlib.sha256(data).hexdigest()}  {archive.name}\n"
    if args.check:
        if archive.read_bytes() != data or checksum.read_text() != line:
            raise SystemExit("Assistant kit ZIP/checksum is stale")
        print("PASS: assistant kit, canonical skill ZIP parity and SHA-256")
    else:
        archive.write_bytes(data)
        checksum.write_text(line)
        print(f"Built {archive.name}: {len(data)} bytes; {line.strip()}")


if __name__ == "__main__":
    main()
