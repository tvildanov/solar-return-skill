# Verification plan

Use synthetic dates and city-centre coordinates only; never commit generated personal reports.

## Packaging (standard library; does not execute calculator)

- `python3 tools/package_skill.py` rebuilds the ZIP from an explicit six-file allowlist.
- `python3 tools/package_skill.py --check` checks root structure, concise frontmatter, syntax, license parity, archive/source equality and checksum.
- Build twice: bytes must be identical. No `.venv`, caches, birth-data outputs or credentials may enter the ZIP.

## Calculator (requires review/approval and dependencies)

- Typical birth/return in separate IANA zones: JSON and human output, 24 contiguous intervals of 86,400 seconds.
- Return longitude agrees with natal Sun within rounding tolerance; this is an internal invariant, not comparison against an independent astronomical reference.
- Leap-day birthday; longitude crossing 0° Aries; rounded sign boundaries.
- DST spring gap rejects; autumn repeated hour requires explicit fold and maps to two distinct UTC instants.
- Non-finite/out-of-range coordinates, unsupported house systems, malformed dates/time zones and unsupported years fail with useful errors.
- Polar Placidus fails explicitly, never silently switches house system; explicit Whole Sign can be tested separately.
- Optional JSON file creation does not overwrite an existing file; metadata identifies assumptions and versions.

## Human installation acceptance

Claude upload/enable/prompt and Claude Code discovery must be checked in actual accounts before claiming end-to-end product compatibility. Windows/macOS compatibility is not proved by Linux tests. Validate upstream astronomy accuracy independently before making stronger accuracy claims.

## Maintenance

Keep `solar-return/VERSION`, README, ZIP and SHA-256 together. Rebuild after every packaged change and inspect the diff. Re-test after dependency updates. Do not commit generated result JSON. Preserve AGPL text and author attribution.
