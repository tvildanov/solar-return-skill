# Verification plan

Use synthetic dates and city-centre coordinates only; never commit generated personal reports.

## Packaging (standard library; does not execute calculator)

- `python3 tools/package_skill.py` rebuilds the ZIP from an explicit file allowlist in `tools/package_skill.py`.
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

## Cross-platform adapters

- `python3 tools/package_plugin.py` synchronizes the generated plugin copy from the canonical skill.
- `python3 tools/package_plugin.py --check` rejects drift, unlisted files and stale archives.
- `tests/test_distribution.py` exercises four host copy destinations (Codex, Cursor, Claude Code, Grok Build) using temporary directories, dry-run, refusal of existing installs and symlink destinations, and marketplace path resolution. No real user profile is modified.
- `tests/test_solar_reference.py` uses recorded synthetic JPL Sun cases with explicitly limited tolerances. It is offline regression coverage, not a fresh external accuracy audit.

## Optional observation instructions

- Check the canonical observation reference survives skill ZIP, plugin ZIP and each temporary host install byte-for-byte.
- Review behavior on a calculation-only request, “I felt nothing”, a skipped entry, a request to prove causation, and a request to infer someone else’s sensations. The assistant should preserve choice, distinguish missing data and avoid inventing experiences or causal/health claims. These are instruction-review scenarios, not proof of behavior in every model.
- Changing observation instructions must not change calculator functions or add note collection, network calls or automatic persistence.


## Assistant kit and conversational contract (0.5.0)

- Run `python3 tools/package_skill.py`, `python3 tools/package_plugin.py`, then `python3 tools/package_assistant_kit.py`. Run each again with `--check`; build twice and compare checksums.
- The assistant kit contains `README-FIRST.md`, five standalone agent instructions, the canonical skill ZIP, and the license. It is a distribution bundle, not a universal installer.
- Distribution tests validate the quoted YAML description (including rejection of the old unquoted colon), exact archive contents, nested skill parity, five identical shared protocols, required privacy/runtime/rectification guards, prompt size, and symlink refusal. They use synthetic files and temporary directories, not real profiles.
- Run `node --test tests/test_prompt.mjs` with Node 18+ for the browser's copied prompt. These are text-contract tests, not proof of model compliance.
- Run `.venv/bin/python -m unittest discover -s tests -v` both normally and with `PYTHONTZPATH=''` to test pinned tzdata. Birth-time tests cover both autumn folds, spring gaps, elapsed-minute spacing, duplicate/pre-birth/out-of-range/skipped event dates, invalid windows, zero scores, tied scores, and honest output labels.
- Smoke-test extracted skill and plugin ZIPs with synthetic calculator and rectification inputs. Never add actual recipients' birth details to fixtures or shared instructions.
- Human acceptance still required: save/upload the right artifact in each actual client/account, confirm discovery, then prove real execution separately. A text upload, Project/Gem/Skill entry or API capability claim is not execution evidence. Test no-runtime, unknown birth time, corrected input, request for numbers only, and setup-only/no-data paths.
