# Solar return: distilled algorithm

This file states every rule the skill uses, so any person, AI model or program can reproduce the same result. The calculator (`scripts/solar_return.py`) and the report builder (`scripts/report.py`) implement exactly these rules; the texts live in `kb.<lang>.json`, the degree table in `degrees.json`.

Labels: **[astronomy]** — computed fact; **[convention]** — a choice of method; **[tradition]** — symbolic rule from astrological practice, not a scientific claim.

## 1. Inputs

- Local birth date and time, birthplace latitude/longitude, IANA time zone of the birthplace.
- Anniversary year.
- Latitude/longitude and IANA time zone of the place where the solar return is met.
- Options: house system (default Placidus), orb for solar-to-natal aspects (default 1°), degree convention (default ordinal), places to compare, latitude + goal house for a longitude scan.

## 2. Calculation [astronomy]

1. Convert local birth time to UTC with the IANA zone history. Reject nonexistent local times; require an explicit fold for repeated ones.
2. Natal chart: tropical geocentric longitudes (Swiss Ephemeris, Moshier mode) of Sun, Moon, Mercury … Pluto, true North Node; houses for the birthplace.
3. Solar-return moment: start at 12:00 UTC on the birthday in the requested year; iterate `t += Δλ / v` (Δλ = natal Sun − current Sun, wrapped to ±180°, v = Sun speed) until |Δλ| < 1e-9°.
4. Solar-return chart: same bodies at that moment; houses for the place where the return is met. For each body record its house in the solar-return chart and in the natal chart.
5. House membership: a longitude belongs to house k if it lies between cusp k (inclusive) and cusp k+1 (exclusive), measured along the zodiac.

## 3. The 24 days [tradition]

- Closing day −k (k = 12…1) starts at `SR − k × 24 h`; opening day +k (k = 1…12) starts at `SR + (k − 1) × 24 h`. Each lasts exactly 86 400 s and is displayed in the local zone of the return place.
- Day ±k corresponds to house k. Closing days review and complete the area; opening days set its tone.
- Highlight: day +1 (start of the cycle), days ±8 (8th house: extra care), and every day whose house holds solar-return planets (Sun…Pluto).

## 4. Aspects [convention]

- Major aspects only: 0°, 60°, 90°, 120°, 180°.
- Inside the solar-return chart: orb 8/5/7/7/8°, wider by 2° when the Sun or Moon is involved (base orbs minus 2° otherwise).
- Solar-return body → natal body or natal ASC/MC: one orb for all aspects (default 1°). SR Sun → natal Sun is always exact and is not reported.

## 5. Keys of the year [tradition, deterministic ranking]

Collect candidate factors with weights, sort by weight, keep the top 7:

| Weight | Factor |
| --- | --- |
| 100 | Solar-return Ascendant sign — the tone of the year |
| 95 | House of the SR Sun — the main arena. If the Moon or a stellium shares the house, merge them into this key |
| 90 + n | Stellium: n ≥ 3 bodies (Sun…Pluto) in one house (if not already merged) |
| 85 | House of the SR Moon (if not merged) |
| 80 − 10 × orb | SR→natal aspect involving SR Sun/Moon or natal Sun/Moon/ASC/MC |
| 70 | Natal houses of the SR Sun and Moon |
| 58–60 | Mercury, Venus, Mars, Jupiter, Saturn in an angular SR house (1, 4, 7, 10) |
| 55 | Uranus, Neptune, Pluto in an angular SR house |
| 50 | Retrograde Mercury, Venus or Mars |

Each key carries: text, light side, shadow side, what helps — taken from the knowledge base for the relevant sign, house, planet or aspect.

## 6. Royal and destructive degrees [tradition]

- Table (`degrees.json`), degree numbers 1–30 within a sign:
  - Royal: Aries 18, Gemini 9, Leo 7, Virgo 25, Scorpio 13, Capricorn 11, Aquarius 30.
  - Destructive: Aries 23, Gemini 13, Leo 10, Libra 1, Scorpio 19, Capricorn 19, Pisces 4.
- Two sources give identical numbers; neither names the original author.
- Convention: **ordinal** (default) — the 13th degree is 12°00′–12°59′; **exact** — 13°00′–13°59′. Sources do not specify; the report states which was used.
- Checked points: all bodies and ASC/MC of both the natal and the solar-return chart.
- Royal: the force is traditionally supported and may bring recognition. Destructive: a vulnerable spot that needs care. Never presented as fate.

## 7. Relocation: where to meet the solar return [astronomy + convention]

- The moment is identical worldwide; only houses and angles change with place.
- For each candidate place report: ASC sign, MC sign, house of Sun and Moon, planets within 5° of ASC/MC/DSC/IC, stelliums.
- Longitude scan: along one latitude, step 1°, list longitude ranges where the SR Sun falls in the goal house, with the ASC signs found there.
- No place is labelled "good" or "bad": the person chooses by intention (Sun house = main arena, ASC = tone, angular planets = stronger).

## 8. Report structure

1. Moment (local, UTC, extra zones). 2. Chart table. 3. Keys of the year. 4. Planets by house. 5. SR→natal aspects. 6. Royal/destructive degrees. 7. Relocation (if requested). 8. The 24 days (closing and opening tables). 9. Meeting the moment. 10. Journal. 11. Method and assumptions.

## 9. Safety rules

- Astrology is a language for reflection, not a validated forecast.
- No medical, legal or financial instructions; no predictions of death, illness or disaster.
- Never invent a birth time or estimate positions by eye.
- Ask before storing or exporting birth data.
