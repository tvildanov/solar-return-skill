# Version 0.5.0 — shareable assistant kit and conversational onboarding

Date: **2026-11-13**. Baseline: `7c71be576ee8c486540ed421f0976adf24d40b7f` (0.4.0). No personal charts or recipient data were used.

## Passed

- **60 Python tests**, both with the system IANA database and with pinned `tzdata==2026.6` forced via `PYTHONTZPATH=''`. Linux x86-64, Python 3.12, `pyswisseph==2.10.3.2` built in an isolated virtual environment using the available GCC toolchain.
- **3 Node prompt-contract tests** for browser output handoff, corrections, runtime honesty, unknown birth-time precision, optional interpretation and privacy. These inspect emitted text, not behavior in every AI model.
- All **19 functions** in the main `solar_return.py` calculator are AST-identical to the baseline. Only its version constant changed. Existing recorded JPL reference tests pass; no new independent astronomy audit was performed.
- Rectification regression tests reproduced the old spring-gap/fold defects before the fix. Windows now step in UTC and display dates/offsets. Duplicate/pre-birth/unsupported/skipped event dates are rejected. Zero/tied scores do not identify a unique birth minute; minute resolution is explicitly not accuracy or probability.
- Fixed invalid YAML in the old skill description (an unquoted colon followed by a space). The frontmatter now passes a real YAML parse; packaging enforces a quoted scalar and a regression test rejects the old malformed value.
- All three deterministic archives and SHA-256 files match their sources. The new assistant kit contains five standalone instructions (Claude, ChatGPT, Grok, Gemini, generic), bilingual start instructions and the exact canonical skill ZIP. Source symlinks are rejected for kit adapters, including the start document and adapter directory.
- Extracted skill ZIP and plugin ZIP each executed a synthetic solar-return report/JSON and repeated-hour rectification smoke test successfully. The report returned the existing reference moment `2026-04-17 10:11:17 America/New_York` for the synthetic Berlin example.
- Four temporary host-install destinations were verified without modifying a real user profile. Canonical conversational and birth-time references survive both skill/plugin packaging. Five standalone protocols are identical and below 8,000 characters, with platform-specific introductions.
- Official platform documentation was checked for the instructions in [PLATFORMS.md](PLATFORMS.md). Local documentation links and `git diff --check` pass.

## Not established by these checks

- No real-account installation or execution was tested in Claude, ChatGPT, Grok or Gemini. No marketplace publication, remote API, merge or deployment is part of this verification. Reading, installing and executing remain separate states.
- A local Chromium smoke test was attempted but the execution sandbox denied browser socket creation before startup. Actual browser UI/clipboard smoke testing for this revision remains **not run**; the copied prompt's three contract tests passed. Browser numerical formulas and rendered report layout were not changed.
- Synthetic event-score tests verify implementation consistency, not real-world rectification validity. No astrological or psychological claim is scientifically validated by this release.
- macOS/Windows and account-specific dependency/network restrictions were not tested. The instructions provide a no-runtime browser fallback without claiming that every AI can execute the calculator.

---

# Version 0.3.0 — distilled algorithm, autonomous report, relocation, rectification, web calculator

- Independent Astropy/ERFA check (`tests/independent_check.py`, 5 synthetic charts): return moment ≤ 2 s; ASC, MC, Moon ≤ 0.04′.
- Synthetic rectification check (`tests/rectify_synthetic.py`): events built from a known minute; stated time off by 23 min; the true minute is recovered exactly.
- Year-by-area table, Moon sign of each day and launch-zone boundary matched an independently prepared reference report (private data, not included).
- Web calculator (`docs/`) reproduces the Python moment and positions to the second (headless Chromium).
- `python3 -m pytest tests`: 43 tests pass.

# Version 0.2.2 — optional observation protocol

Date: **2026-10-31**. Adds a short, author-approved AstroEmpathy observation adaptation: calculated data, symbolic themes and reported body/emotion/attention experience stay separate. Participation, every entry and sharing are optional. There is no causal or medical claim, new data collection or automatic note storage.

## Passed for this version

- **32/32 synthetic tests** with the system IANA database (1.476 seconds), and **32/32** with pinned `tzdata` forced (1.463 seconds). Real `pyswisseph==2.10.3.2`; isolated Linux x86-64 / Python 3.12.14.
- All **18 calculator functions are AST-identical to 0.2.1**; only the version constant/comment changed. Existing recorded JPL Sun cases pass offline; no fresh external astronomy comparison was performed for this documentation release.
- The observation reference is linked from `SKILL.md`, included byte-for-byte in both archives, and copied by the existing three-host installer tests in temporary projects. The canonical skill now has a seven-file allowlist.
- Both deterministic ZIPs match their source and SHA-256. Each extracted archive executes a synthetic January-1 case, gives the same result/24-day JSON and includes the observation reference.
- Skill frontmatter validator, Python 3.9 grammar parsing, official Agent Plugins manifest schema and changed documentation's local links pass.
- Independent instruction review covered calculation-only, no sensation, skipped entries, causal-inference requests and another person's unreported feelings. Clarified the calculation-only override and removed two predictive-sounding prompts. This is a bounded text review, not a cross-model behavioral guarantee.

**Not performed:** real-account skill/plugin import, marketplace submission, macOS/Windows testing, medical/psychological validation or a new astronomical audit. No user profile was modified, no observation reports were collected, and no remote service was deployed. Prior accuracy limits and platform caveats still apply.

---

# Earlier 0.2.1 — compatibility and limited accuracy verification

Date: **2026-10-30**. Canonical skill and plugin both package calculator 0.2.1. The solver, chart formulas and 24-day method are unchanged; anniversary-year help/output and provenance metadata are clarified.

## Passed for this version

- **31/31 tests**, system IANA database (1.422 seconds), and **31/31** with pinned `tzdata` forced (1.505 seconds).
- Eight new distribution tests: copies for Codex/Cursor/Claude Code in temporary projects, exact file allowlist, dry-run without writes, refusal to overwrite and refusal of symlink destinations; both catalogs resolve the same plugin.
- Two reference test methods cover eight recorded synthetic JPL Sun cases and both January/December year-boundary semantics. [Accuracy report and limitations](ACCURACY.md).
- Portable `plugin.json` validated against the official [Agent Plugins 1.0 JSON schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json); all referenced local paths resolve. This is format validation, **not a successful import into every host**.
- Both ZIPs are deterministic and source-matched; the generated plugin skill is identical to the canonical skill. Both extracted archives execute on a synthetic January-1 case, display the adjacent-year notice and produce versioned 24-day JSON.
- Python 3.9 grammar checked; runtime tested on isolated Linux / Python 3.12.14. [Platform-specific steps](PLATFORMS.md) were checked against official documentation, not every client UI.

**Not performed:** real-account plugin import/installation in ChatGPT, Cursor or Claude; marketplace submission; macOS/Windows runtime testing; independent validation of every planet, house or interpretation. No user profile was modified by adapter tests, no remote calculation server was deployed, and the installer never installs dependencies or executes the calculator.

---

# Earlier 0.2.0 verification — 2026-10-30

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

## Not established by those earlier tests

- The earlier tests did not independently validate astronomy. The subsequent limited JPL Sun comparison is documented in [ACCURACY.md](ACCURACY.md).
- Scientific validity of astrological interpretations.
- Live upload/activation in a user's Claude account or Claude Code UI.
- Runtime compatibility on Windows, macOS, every Python version or every host/account policy.

See `TESTING.md` for repeatable checks, and `solar-return.zip.sha256` for the artifact digest. Rebuild and re-test whenever packaged source changes; do not treat this dated record as evidence for later versions.
