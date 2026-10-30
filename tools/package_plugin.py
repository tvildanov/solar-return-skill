#!/usr/bin/env python3
"""Build/check the portable plugin from the canonical skill allowlist."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
from package_skill import FILES, ROOT, build_bytes

PLUGIN = ROOT / 'plugins/solar-return'


def expected_files():
    build_bytes()  # validates canonical skill without executing calculator
    manifest = json.loads((PLUGIN / 'plugin.json').read_text())
    if manifest['name'] != 'solar-return' or manifest['version'] != (ROOT / 'solar-return/VERSION').read_text().strip():
        raise ValueError('plugin identity/version does not match skill')
    if manifest['$schema'] != 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json':
        raise ValueError('unexpected plugin schema')
    files = {'plugin.json': (PLUGIN / 'plugin.json').read_bytes(),
             'README.md': (PLUGIN / 'README.md').read_bytes(),
             'LICENSE': (ROOT / 'LICENSE').read_bytes()}
    for source in FILES:
        files['skills/' + source] = (ROOT / source).read_bytes()
    return files


def archive_bytes(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        for relative, data in sorted(files.items()):
            info = zipfile.ZipInfo('solar-return-plugin/' + relative, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    files = expected_files()
    data = archive_bytes(files)
    archive = ROOT / 'solar-return-plugin.zip'
    checksum = ROOT / 'solar-return-plugin.zip.sha256'
    line = hashlib.sha256(data).hexdigest() + '  solar-return-plugin.zip\n'
    if args.check:
        actual = {str(p.relative_to(PLUGIN)) for p in PLUGIN.rglob('*') if p.is_file()}
        if actual != set(files):
            raise SystemExit('Plugin tree has missing or unlisted files')
        if any((PLUGIN / name).is_symlink() or (PLUGIN / name).read_bytes() != content for name, content in files.items()):
            raise SystemExit('Plugin copy is stale; rebuild from canonical skill')
        if archive.read_bytes() != data or checksum.read_text() != line:
            raise SystemExit('Plugin ZIP/checksum is stale')
        print('PASS: portable plugin tree, canonical skill parity, deterministic archive and SHA-256')
    else:
        for name, content in files.items():
            target = PLUGIN / name
            if target.is_symlink():
                raise ValueError('Refusing symlink output: ' + str(target))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        archive.write_bytes(data)
        checksum.write_text(line)
        print(f'Built {archive.name}: {len(data)} bytes; {line.strip()}')


if __name__ == '__main__':
    main()
