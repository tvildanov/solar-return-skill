# Version 0.2.0 verification — 2026-10-30

Test environment: isolated Linux x86-64, Python 3.12.14, `pyswisseph==2.10.3.2`, `tzdata==2026.6`. No personal birth records used. No end-user computer or AI-account installation performed.

## Passed

- 21 calculator tests using the real Swiss Ephemeris dependency, 1.401 seconds.
- The same 21 tests with `PYTHONTZPATH=''` to force pinned `tzdata`, 1.427 seconds.
- Three synthetic scenarios (ordinary birthday, leap-day birthday, near Aries) produce exactly the upstream core JSON for natal/solar charts, aspects, 24 days and UTC/local moments. Upstream baseline: `62fd4295e3bcec22f8d66e9b040eec57a8053690`.
- Regression reproduction before changes: zodiac sign carry, nonexistent spring-DST input, and minute rounding across an autumn clock transition. See `tests/original_regressions.txt`.
- Input errors, explicit DST folds, polar-house errors, solver failure, no-overwrite/symlink rejection, private POSIX report mode, metadata and version covered by unit tests.
- Packaged Python syntax and Python 3.9 grammar compatibility checked. Actual runtime test was Python 3.12, not every supported interpreter.
- Reproducible ZIP: two builds are byte-identical; explicit six-file allowlist, one `solar-return/` root, valid concise frontmatter, original license, source parity and SHA-256 checked.
- Extracted ZIP executed on a separate synthetic example in Russian and generated a valid 24-day JSON report. Temporary output was deleted after the test.

Native dependency installation on this environment required available GCC/G++ overrides because the runtime's default Clang tools were absent. This was a build-environment issue, not a calculator change; no operating-system packages were installed.

## Not established by these tests

- Independent astronomical accuracy against another ephemeris: agreement with the same engine and upstream is a regression check, not an independent reference.
- Scientific validity of astrological interpretations.
- Live upload/activation in a user's Claude account or Claude Code UI.
- Runtime compatibility on Windows, macOS, every Python version or every host/account policy.

See `TESTING.md` for repeatable checks, and `solar-return.zip.sha256` for the artifact digest. Rebuild and re-test whenever packaged source changes; do not treat this dated record as evidence for later versions.
