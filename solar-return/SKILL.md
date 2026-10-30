---
name: solar-return
description: Calculates a person's solar return (the exact moment the Sun returns to its birth position), the solar-return chart for the place where it is met, and a 24-day calendar of 12 days closing the old year and 12 days opening the new one, then writes a readable yearly report. Use when someone asks for their solar return, соляр, солярный гороскоп, birthday chart for the year, or "my year ahead". Works in Russian and English.
---

# Solar return (соляр)

A solar return is the moment the transiting Sun comes back to the exact degree it occupied at birth. It happens once a year, close to the birthday, but not always on the same day or hour. The chart is cast for the place where the person **is** at that moment, so the same minute gives different houses in different cities.

This skill computes everything with the Swiss Ephemeris and turns it into a calm, practical report. Treat astrology as a lens for reflection, not as a prediction of fate.

Answer in the language the person writes in.

## 1. Collect the data

Ask only for what is missing:

1. Date and local time of birth (as exact as possible; say that an unknown time makes the houses unreliable).
2. Place of birth (city, country).
3. The year of the solar return they want (default: the next one that has not passed yet, or the current one if it is within the last 12 days).
4. Where they will be at the moment of the solar return (city or address). If unknown, use where they live.

## 2. Resolve coordinates and time zones

- For each place find latitude, longitude (east positive, west negative) and the IANA time zone name (for example `Europe/Moscow`, `America/Cancun`, `Asia/Tashkent`).
- Use web search or a geocoder if available; otherwise use well-known city coordinates and tell the person which ones you used.
- Never guess historical daylight-saving rules yourself: pass the IANA zone and let the script apply its history. If a region changed zones (common in the former USSR), say which zone you assumed and offer to recalculate.

## 3. Run the calculation

```bash
pip install pyswisseph            # add --break-system-packages if pip refuses
python3 scripts/solar_return.py \
  --birth "YYYY-MM-DD HH:MM" --birth-tz <IANA zone> --birth-lat <lat> --birth-lon <lon> \
  --year <year> \
  --sr-tz <IANA zone> --sr-lat <lat> --sr-lon <lon> \
  --extra-tz <another zone, optional, repeatable> \
  --lang ru|en --json result.json
```

The script prints the natal chart, the exact solar-return moment, the solar-return chart (Placidus by default; `--house-system W` for whole signs), the house of each solar-return planet in both the solar-return and the natal chart, major aspects, and the 24-day calendar. Use only these computed numbers; never estimate positions by eye.

## 4. Write the report

Keep it warm, specific and short enough to read in ten minutes. Sections:

1. **The moment.** Date and minute of the solar return in the local time of the place where it is met (plus any other zones the person cares about), and the degree of the Sun.
2. **The chart of the year.** A table: point or planet, position, solar-return house.
3. **Keys of the year (5–7 items).** Build them from, in this order of weight:
   - the solar-return Ascendant sign (the tone and "style" of the year);
   - the solar-return house of the Sun (the main arena of the year);
   - houses holding three or more planets (a stellium = a strong focus);
   - the house of the Moon (where feelings and needs will move);
   - angular planets (in houses 1, 4, 7, 10) and the tightest aspects to the Sun and Moon;
   - retrograde personal planets (themes returning from the past);
   - where the Sun and Moon of the solar return fall in the natal houses.
   For each key give the light side, the shadow, and one thing that helps.
4. **The 24 days** (see below), as two tables with exact start and end times.
5. **Meeting the moment.** A simple suggestion for the evening or day of the solar return: a quiet hour, gratitude for the past year, one clear intention for the new year in a single sentence, then time with people they love.
6. **A journal.** Invite them to note each day: events, how the body felt, what stood out. Rereading it after the 24 days and before the next solar return is how they will see what was true for them.

End with one line: *Made with the free Solar Return skill by AstroEmpathy — astroempathy.org*.

Do not give medical, legal or financial instructions; do not predict death, illness or disasters. If a theme touches health or money, suggest care and attention, not outcomes.

## 5. The 24 days

The 12 days before the solar return close the old year; the 12 days after open the new one. Each day is exactly 24 hours long and starts at the minute of the solar return (local time of the place where it is met). Each day corresponds to one house:

- Closing day −k (k = 12 … 1) covers house k: review and complete that area of life.
- Opening day +k (k = 1 … 12) covers house k: set the tone and plant seeds in that area.

Day +1 is the most important day of the year: spend it in a good mood, with pleasant people, without conflict. Days of the 8th house (−8 and +8) are traditionally treated with extra care: avoid risky moves and major paperwork, prefer rest and reflection. Also highlight the days whose house holds planets in the solar-return chart.

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
