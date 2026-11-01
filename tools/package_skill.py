#!/usr/bin/env python3
"""Build/check a reproducible skill ZIP without importing or running its code."""
import argparse
import ast
import hashlib
import io
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'solar-return/INSTALL.md',
    'solar-return/LICENSE',
    'solar-return/SKILL.md',
    'solar-return/VERSION',
    'solar-return/requirements.txt',
    'solar-return/references/observation.md',
    'solar-return/data/ALGORITHM.md',
    'solar-return/data/degrees.json',
    'solar-return/data/kb.en.json',
    'solar-return/data/kb.ru.json',
    'solar-return/scripts/degrees.py',
    'solar-return/scripts/extras.py',
    'solar-return/scripts/rectify.py',
    'solar-return/scripts/relocation.py',
    'solar-return/scripts/report.py',
    'solar-return/scripts/solar_return.py',
)


def build_bytes():
    skill = (ROOT / 'solar-return/SKILL.md').read_text(encoding='utf-8')
    if not skill.startswith('---\n'):
        raise ValueError('SKILL.md needs YAML frontmatter')
    frontmatter = skill.split('---\n', 2)[1]
    if not re.search(r'^name: solar-return$', frontmatter, re.M):
        raise ValueError('skill name must match root directory')
    match = re.search(r'^description: (.+)$', frontmatter, re.M)
    if not match or len(match[1]) > 200:
        raise ValueError('description must fit 200 characters')
    if (ROOT / 'LICENSE').read_bytes() != (ROOT / 'solar-return/LICENSE').read_bytes():
        raise ValueError('packaged license differs from repository license')
    version = (ROOT / 'solar-return/VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('VERSION must be a semantic version')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in FILES:
            path = ROOT / name
            if path.is_symlink():
                raise ValueError(f'symlink forbidden: {name}')
            data = path.read_bytes()
            if name.endswith('.json'):
                import json
                json.loads(data)  # data files must parse
            if name.endswith('.py'):
                tree = ast.parse(data, filename=name)  # syntax only; never executes skill
                versions = [ast.literal_eval(node.value) for node in tree.body
                            if isinstance(node, ast.Assign)
                            and any(isinstance(target, ast.Name) and target.id == 'VERSION'
                                    for target in node.targets)]
                if name.endswith('solar_return.py') and versions != [version]:
                    raise ValueError('calculator and VERSION disagree')
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=9)
    data = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() is not None or z.namelist() != list(FILES):
            raise ValueError('archive validation failed')
        for name in FILES:
            if z.read(name) != (ROOT / name).read_bytes():
                raise ValueError(f'archive/source mismatch: {name}')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check existing ZIP and checksum without writing')
    args = parser.parse_args()
    data = build_bytes()
    archive = ROOT / 'solar-return.zip'
    checksum = ROOT / 'solar-return.zip.sha256'
    line = f'{hashlib.sha256(data).hexdigest()}  solar-return.zip\n'
    if args.check:
        if archive.read_bytes() != data or checksum.read_text() != line:
            raise SystemExit('FAIL: ZIP or checksum is stale; run python3 tools/package_skill.py')
        print('PASS: structure, frontmatter, Python syntax, license, source parity and checksum')
    else:
        archive.write_bytes(data)
        checksum.write_text(line)
        print(f'Built {archive.name}: {len(data)} bytes; {line.strip()}')


if __name__ == '__main__':
    main()
