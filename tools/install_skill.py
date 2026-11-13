#!/usr/bin/env python3
"""Copy the reviewed skill to a chosen local host; no downloads or execution."""
import argparse
from pathlib import Path
import shutil
import sys

from package_skill import FILES, ROOT

HOST_DIRS = {'codex': '.agents', 'cursor': '.cursor', 'claude-code': '.claude', 'grok-build': '.grok'}


def install(host, base, *, dry_run=False, source_root=ROOT):
    base = Path(base).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise ValueError('The selected project/home must be an existing directory.')
    destination = base / HOST_DIRS[host] / 'skills' / 'solar-return'
    for directory in [base / HOST_DIRS[host], destination.parent, destination]:
        if directory.is_symlink():
            raise ValueError(f'Refusing symlink destination: {directory}')
    if destination.exists():
        raise FileExistsError(f'Already installed at {destination}. Back it up and choose how to update; nothing was overwritten.')
    payload = []
    for filename in FILES:
        source = source_root / filename
        if source.is_symlink() or any(p.is_symlink() for p in source.parents if p != source_root.parent):
            raise ValueError(f'Refusing symlink source: {source}')
        payload.append((Path(filename).relative_to('solar-return'), source.read_bytes()))
    if dry_run:
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()  # fail closed if another process installed it meanwhile
    try:
        for relative, content in payload:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(content)
    except Exception:
        shutil.rmtree(destination)  # only this new, incomplete installation
        raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, choices=tuple(HOST_DIRS))
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument('--project', type=Path, help='existing project directory; never inferred')
    scope.add_argument('--user', action='store_true', help='install for the current OS user')
    parser.add_argument('--dry-run', action='store_true', help='show destination, write nothing')
    args = parser.parse_args()
    try:
        destination = install(args.host, Path.home() if args.user else args.project, dry_run=args.dry_run)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(('Would copy to ' if args.dry_run else 'Copied to ') + str(destination))
    print('No dependencies installed and no calculator executed. Review requirements and host permissions before running.')


if __name__ == '__main__':
    main()
