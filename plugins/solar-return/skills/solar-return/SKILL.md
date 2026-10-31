---
name: solar-return
description: Calculate a solar return (соляр), yearly chart and 12-before/12-after day calendar in Russian or English. Use for explicit solar-return requests; requires Python execution.
---

# Solar return (соляр)

A solar return is the moment the transiting Sun comes back to the exact degree it occupied at birth. It happens once a year, close to the birthday, but not always on the same day or hour. The chart is cast for the place where the person **is** at that moment, so the same minute gives different houses in different cities.

This skill computes astronomical positions using Swiss Ephemeris in built-in Moshier mode and turns them into a calm, practical astrological report. Astrology is a lens for reflection, not a scientifically validated forecast. Preserve the original 12-before/12-after method; do not substitute an unrelated solar-return tradition.

Answer in the language the person writes in.

Keep **calculated astronomy**, **symbolic interpretation** and **reported subjective experience** visibly separate throughout the report. Offer the optional AstroEmpathy observation approach in [references/observation.md](references/observation.md) only if the person wants it. Read that reference before guiding an exercise; do not infer sensations from the chart or present observations as evidence of celestial causation. A calculation-only report needs no journal.

## 1. Collect the data

Ask only for what is missing:

1. Date and local time of birth (as exact as possible). If the time is unknown, explain that both the return time and houses are uncertain; do not invent a time or present a precise chart. A provisional time-based scenario requires the user to explicitly choose and acknowledge the assumption.
2. Place of birth (city, country).
3. The birthday-anniversary year they want. `--year` searches near that anniversary; the event may fall in the preceding/following calendar year. If they mean an event strictly within January–December, clarify rather than silently changing the meaning (default: the next one that has not passed yet, or the current one if it is within the last 12 days).
4. Where they will be at the moment of the solar return (city and country are enough). If unknown, ask whether to use their current city; do not infer their location. Do not request a full name or home address.

Before collecting data, explain that the AI host processes chat data and that an optional JSON export stores birth data and coordinates. Do not claim that data stays private or local in a hosted chat. Use only data the person is comfortable sharing, and never include it in repository files.

## 2. Resolve coordinates and time zones

- For each place find latitude, longitude (east positive, west negative) and the IANA time zone name (for example `Europe/Moscow`, `America/Cancun`, `Asia/Tashkent`).
- Use a verified coordinate/time-zone source when available. Search only for city/country, never send birth date, birth time or a street address to a geocoder. Explain external lookup use before sharing location data. Otherwise state any approximate city-centre coordinates and ask the user to confirm the assumption.
- Never guess historical daylight-saving rules yourself: pass the IANA zone and let the script apply its history. If a region changed zones (common in the former USSR), say which zone you assumed and offer to recalculate.

## 3. Run the calculation

Resolve paths relative to this installed skill folder, not the current project. Use an existing suitable Python environment where possible. Follow the host's approval requirements before installing dependencies or executing downloaded code. If execution is unavailable, state that the chart was not calculated; never fabricate a result.

For local setup use an isolated environment (`python3 -m venv <writable-env-path>`) and its Python with `-m pip install -r <skill-folder>/requirements.txt`. Never use `sudo pip`, modify system Python, or bypass a failed permission check. See [INSTALL.md](INSTALL.md).

Run with that environment's Python (the example assumes the working directory is the skill folder):

```bash
python scripts/solar_return.py \
  --birth "YYYY-MM-DD HH:MM" --birth-tz <IANA zone> --birth-lat <lat> --birth-lon <lon> \
  --year <year> \
  --sr-tz <IANA zone> --sr-lat <lat> --sr-lon <lon> \
  --extra-tz <another zone, optional, repeatable> \
  --lang ru|en
```

Use `--json <new-path>` only when the user wants an export; it stores their original inputs. Do not overwrite a result file or upload it without permission. For a repeated local birth hour the script requires `--birth-fold 0` (earlier occurrence) or `1` (later); ask which UTC offset the record means. A nonexistent local time must be corrected, not silently shifted.

The script prints the natal chart, the exact solar-return moment, the solar-return chart (Placidus by default; `--house-system W` for whole signs), the house of each solar-return planet in both the solar-return and the natal chart, major aspects, and the 24-day calendar. Use only these computed numbers; never estimate positions by eye. If Placidus fails at a polar latitude, explain the limitation and ask before switching explicitly to Whole Sign. State the house system, location assumptions and ephemeris mode in the report. Numerical output is not an independent accuracy certificate. UTC is approximated as UT1 and all dates use the proleptic Gregorian calendar. Historical and distant-future results need extra caution; see the repository accuracy report. Validation of the Sun does not validate every planet, node, house or interpretation.

## 4. Write the report

For a calculation-only request, provide the computed moment, chart and requested calendar with assumptions; omit symbolic interpretation, exercises and journal invitations. Otherwise keep the report warm, specific and short enough to read in ten minutes. Sections:

1. **The moment.** Date and minute of the solar return in the local time of the place where it is met (plus any other zones the person cares about), and the degree of the Sun.
2. **The chart of the year.** A table: point or planet, position, solar-return house.
3. **Keys of the year (5–7 items).** Build them from, in this order of weight:
   - the solar-return Ascendant sign (the tone and "style" of the year);
   - the solar-return house of the Sun (the main arena of the year);
   - houses holding three or more planets (a stellium = a strong focus);
   - the house of the Moon (an optional symbolic theme for exploring feelings and needs);
   - angular planets (in houses 1, 4, 7, 10) and the tightest aspects to the Sun and Moon;
   - retrograde personal planets (an optional prompt to reflect on past themes);
   - where the Sun and Moon of the solar return fall in the natal houses.
   For each key give the light side, the shadow, and one thing that helps.
4. **The 24 days** (see below), as two tables with exact start and end times.
5. **Meeting the moment (optional).** Offer quiet time, gratitude, one intention or time with people they love if these suit them. No exact-minute ritual or particular feeling is required.
6. **Observation (optional).** Ask whether they want to note body, emotion and attention using the linked AstroEmpathy approach. If yes, offer a neutral baseline before the symbolic reading where practical, and keep original notes separate from later meaning. Rereading may support personal reflection, not prove a prediction; record unchanged experience and mismatches as well. Never require daily entries or auto-save them.

End with one line: *Made with the free Solar Return skill by AstroEmpathy — astroempathy.org*.

Do not give medical, legal or financial instructions; do not predict death, illness or disasters. If a theme touches health or money, suggest care and attention, not outcomes.

## 5. The 24 days

Within this symbolic method, the 12 days before the solar return represent closing the old year; the 12 days after represent opening the new one. Each day is exactly 24 elapsed hours long, anchored to the return instant in UTC, and then displayed in the local time zone. When daylight-saving time changes, the local clock hour may shift; do not claim every interval starts at the same local hour. Each day corresponds to one house:

- Closing day −k (k = 12 … 1) covers house k: review and complete that area of life.
- Opening day +k (k = 1 … 12) covers house k: set the tone and plant seeds in that area.

Within this symbolic tradition, day +1 marks the opening of the cycle: suggest a gentle intention, pleasant company or quiet time without demanding a particular mood. Days of the 8th house (−8 and +8) can prompt reflection on change and shared resources. Do not advise postponing medical care, legal paperwork, payments or important decisions on astrological grounds. Also highlight the days whose house holds planets in the solar-return chart, as optional journaling themes rather than predictions.

| House | Area of life (EN) | Сфера жизни (RU) |
| --- | --- | --- |
| 1 | Self, body, appearance, new beginnings | Личность, тело, образ, новые начала |
| 2 | Money, values, possessions, self-worth | Деньги, ценности, имущество, самооценка |
| 3 | Communication, learning, siblings, neighbours, short trips | Общение, учёба, братья и сёстры, соседи, короткие поездки |
| 4 | Home, family, roots, parents | Дом, семья, корни, родители |
| 5 | Love, creativity, children, joy and play | Любовь, творчество, дети, радость и игра |
| 6 | Health, daily work, routines, service | Здоровье, повседневная работа, режим, забота о других |
| 7 | Partnership, marriage, contracts, open rivals | Партнёрство, брак, договоры, открытые соперники |
| 8 | Crises and transformation, shared resources, deep change | Кризисы и перемены, общие ресурсы, глубокая трансформация |
| 9 | Worldview, travel, higher learning, law | Мировоззрение, путешествия, высшее образование, закон |
| 10 | Career, status, goals, authority | Карьера, статус, цели, руководство |
| 11 | Friends, communities, hopes and plans | Друзья, сообщества, надежды и планы |
| 12 | Solitude, rest, inner life, letting go | Уединение, отдых, внутренняя жизнь, отпускание |

For each day give: number, start → end, house and area, one short suggestion for closing (−) or opening (+).
