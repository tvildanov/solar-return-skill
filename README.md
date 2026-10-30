# Solar Return skill for Claude · Навык «Соляр» для Claude

**RU** · [EN](#english)

Бесплатный навык для Claude: рассчитывает ваш соляр — точную минуту, когда Солнце возвращается в положение рождения, — строит карту года для места, где вы его встречаете, и составляет календарь 24 суток: 12 суток закрытия старого года и 12 суток открытия нового. На выходе — понятный отчёт о темах года и о том, как прожить эти дни.

Расчёт точный: Swiss Ephemeris, с учётом исторических часовых поясов и летнего времени.

## Как установить

### В приложении Claude (claude.ai, компьютер или телефон)

1. Скачайте `solar-return.zip` со страницы [Releases](../../releases/latest).
2. В Claude откройте **Customize → Skills** и загрузите этот ZIP.
3. Убедитесь, что в настройках включено выполнение кода (code execution) — без него навык не сможет посчитать карту.
4. Напишите в чате: «Рассчитай мой соляр» — и ответьте на вопросы о дате, времени и месте рождения и о месте, где встретите соляр.

Подробнее: [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) · [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

### В Claude Code

```bash
git clone https://github.com/tvildanov/solar-return-skill
cp -r solar-return-skill/solar-return ~/.claude/skills/
pip install pyswisseph
```

### Только скрипт расчёта

```bash
pip install pyswisseph
python3 solar-return/scripts/solar_return.py \
  --birth "1990-05-21 14:30" --birth-tz Europe/Moscow --birth-lat 55.7558 --birth-lon 37.6173 \
  --year 2026 --sr-tz Europe/Moscow --sr-lat 55.7558 --sr-lon 37.6173 --lang ru
```

## Что внутри

- `solar-return/SKILL.md` — инструкции для Claude: какие данные спросить, как считать, как написать отчёт.
- `solar-return/scripts/solar_return.py` — расчёт натала, момента соляра, карты соляра, аспектов и 24 суток.

Навык не хранит и никуда не отправляет ваши данные: всё считается в вашей сессии с Claude.

## Поддержать проект

Навык сделан командой [AstroEmpathy](https://astroempathy.org). Если он оказался полезен — поставьте звезду ⭐ репозиторию и расскажите друзьям.

<!-- DONATE: ссылка для донатов будет добавлена -->

## Лицензия

[GNU AGPL v3](LICENSE). Расчёты используют [Swiss Ephemeris](https://www.astro.com/swisseph/) (© Astrodienst AG) через [pyswisseph](https://github.com/astrorigin/pyswisseph), которые распространяются под AGPL. Астрология здесь — инструмент размышления, а не предсказание судьбы.

---

## English

A free skill for Claude that calculates your **solar return** — the exact minute the Sun comes back to its birth position — casts the chart of the year for the place where you meet it, and builds a **24-day calendar**: 12 days closing the old year and 12 days opening the new one. You get a readable report on the themes of the year and how to live those days.

Precise calculation: Swiss Ephemeris, with historical time zones and daylight saving applied.

### Install in the Claude app (claude.ai, desktop or mobile)

1. Download `solar-return.zip` from [Releases](../../releases/latest).
2. In Claude open **Customize → Skills** and upload the ZIP.
3. Make sure code execution is enabled — the skill needs it to compute the chart.
4. Ask: "Calculate my solar return", then answer the questions about your birth data and where you will be on your birthday.

More: [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) · [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

### Install in Claude Code

```bash
git clone https://github.com/tvildanov/solar-return-skill
cp -r solar-return-skill/solar-return ~/.claude/skills/
pip install pyswisseph
```

### Support

Made by [AstroEmpathy](https://astroempathy.org). If it helped you, star ⭐ the repo and share it.

### License

[GNU AGPL v3](LICENSE). Uses the [Swiss Ephemeris](https://www.astro.com/swisseph/) (© Astrodienst AG) via [pyswisseph](https://github.com/astrorigin/pyswisseph), both AGPL. Astrology here is a tool for reflection, not a prediction of fate.
