# Solar Return · Соляр

**English** · **[Русский](README.ru.md)**

A free solar-return toolkit by **[AstroEmpathy](https://astroempathy.org)**: the exact moment the Sun returns to its birth position, the chart of the year for the place where you meet it, and the 24-day calendar — 12 days closing the old year and 12 days opening the new one. Version **0.5.0**.

## One package to share with friends

Download **[solar-return-assistant-kit.zip](https://github.com/tvildanov/solar-return-skill/raw/main/solar-return-assistant-kit.zip)** · [SHA-256](solar-return-assistant-kit.zip.sha256)

Unzip it and open `README-FIRST.md`. It contains ready-to-use instructions for **Claude, ChatGPT, Grok, Gemini and other agents**, plus the full `solar-return.zip` calculator skill. Choose your agent's file and follow its upload/paste instructions. **The kit is not a universal installer:** native skill support and permission to execute Python vary by account. A plain chat can guide you and interpret output from the browser calculator.

The assistant asks only for missing details, explains the result, accepts corrections in the same conversation, and offers optional birth-time sensitivity/rectification without claiming to discover an exact historical time. You calculate your own chart with your own agent; no personal birth data is included in the package.

[Start here](START.md) · [Choose a platform](PLATFORMS.md) · [Standalone conversation adapters](adapters/README.md)

## Online calculator — nothing to install

**[tvildanov.github.io/solar-return-skill](https://tvildanov.github.io/solar-return-skill/)**

Runs entirely in your browser on the Swiss Ephemeris: the moment to the second, chart of the year, keys of the year, the year by area, royal and destructive degrees, the 24 days with the Moon sign of each day, new and full moons. **"Copy prompt for any AI"** packs the precise data into text you can paste into ChatGPT, Gemini, Claude, Grok, DeepSeek or any other AI to get a reading in any of 18 languages. Your birth date and time are never sent anywhere; city search sends only the city name to Open-Meteo.

## The skill for AI agents

Download **[solar-return.zip](https://github.com/tvildanov/solar-return-skill/raw/main/solar-return.zip)** · [SHA-256](solar-return.zip.sha256)

- **Claude app:** upload the ZIP in **[Customize → Skills](https://claude.ai/customize/skills)**, enable it and code execution, then ask *"Calculate my solar return for 2027; ask for missing details first."* ([Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) · [Custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills))
- **Claude Code, Codex, Cursor and other Agent Skills hosts:** see [PLATFORMS.md](PLATFORMS.md) and [START.md](START.md); a portable [plugin ZIP](https://github.com/tvildanov/solar-return-skill/raw/main/solar-return-plugin.zip) is included.
- **Any other AI:** use the online calculator and its prompt button.

### What it does

| Feature | How |
| --- | --- |
| Exact solar return, natal and solar-return charts, 16 house systems | `scripts/solar_return.py`, `--house-system` |
| Autonomous report without AI or internet | `--report` (rules in [ALGORITHM.md](solar-return/data/ALGORITHM.md), texts in `kb.<lang>.json`) |
| Year by area: solar-return house → natal house | in `--report` |
| Solar-return to natal aspects | `--natal-orb` (default 1°) |
| Royal and destructive degrees | in `--report`, `--degree-convention ordinal\|exact` |
| Moon sign of each day; new and full moons within the 24 days | in `--report` and `--diary` |
| Where to meet the return: compare cities, scan longitudes, nearest point to home with the wanted Sun house, "Sun on Ascendant" point, launch plan | `--place`, `--scan-lat --goal-house`, `--home --launch-house --radius-km` |
| Deep layer: need, mechanism and five layers of daily life (body, feelings, thoughts, actions, reactions) for every key; the recipe of the year | in `--report` (`deep.<lang>.json`) |
| Printable observation diary with the zero-degree switch of the year's goal | `--diary` |
| Optional birth-time sensitivity and heuristic ranking (minute resolution, not validated accuracy) | `scripts/rectify.py --window 60 --event "YYYY-MM-DD\|label"` |

### Run locally

```bash
git clone https://github.com/tvildanov/solar-return-skill.git
cd solar-return-skill
python3 -m venv .venv && .venv/bin/python -m pip install -r solar-return/requirements.txt
.venv/bin/python solar-return/scripts/solar_return.py \
  --birth "1990-05-21 14:30" --birth-tz Europe/Moscow --birth-lat 55.7558 --birth-lon 37.6173 \
  --year 2026 --sr-tz Europe/Moscow --sr-lat 55.7558 --sr-lon 37.6173 --report --lang en
```

Do not use `sudo pip` or modify system Python.

## Accuracy

- Independent check against NASA/JPL: return moment within 1.75 s for six modern cases ([ACCURACY.md](ACCURACY.md)).
- Independent check against Astropy/ERFA (`tests/independent_check.py`, five charts): return moment within 2 s; Ascendant, MC and Moon within 0.04′.
- The browser calculator reproduces the Python results to the second.
- Royal/destructive degree table: two sources agree on the numbers; neither names the original author, and the ordinal/exact convention is not stated — the report says which one was used.

Astrology here is a language for reflection, not a scientifically validated forecast. No medical, legal or financial advice.

## Privacy

The Python scripts make no network requests. The browser downloads code and data; city search sends a city query to Open-Meteo. Birth inputs are not sent by the calculator, but pasting a report or prompt into an AI shares it with that AI service. The AI host processes whatever you type into it; `--json` writes your inputs to a local file. Do not publish birth data of other people without consent.

## License

[GNU AGPL v3](LICENSE). Uses the [Swiss Ephemeris](https://www.astro.com/swisseph/) (© Astrodienst AG) via [pyswisseph](https://pypi.org/project/pyswisseph/) and [@swisseph/browser](https://www.npmjs.com/package/@swisseph/browser), both AGPL. Location search in the web calculator: [Open-Meteo](https://open-meteo.com/) with GeoNames data. Made by [AstroEmpathy](https://astroempathy.org) — if it helps you, star ⭐ the repository and share it.
