# Solar Return · Начните здесь / Start here

Этот набор нужен, чтобы **самостоятельно подключить помощника к своему агенту**, а не отправлять кому-то личные данные для расчёта. Одна методика AstroEmpathy, один вычислитель, отдельные инструкции для разных интерфейсов. Никаких API-ключей или регистрации в этом проекте не требуется.

## Русский

1. Если вы получили `solar-return-assistant-kit.zip`, **распакуйте его у себя**. Не нужно загружать весь набор в каждый чат. Внутри лежат файлы ниже и отдельный `solar-return.zip` для поддерживаемых skill-хостов.
2. Выберите файл: `chatgpt.md`, `claude.md`, `grok.md`, `gemini.md` или `any-agent.md` для другого ассистента. В репозитории они находятся в `adapters/`; в распакованном наборе — рядом с этим `README-FIRST.md`.
3. Откройте выбранный файл в текстовом редакторе и **вставьте весь текст в новый разговор**. Либо приложите этот `.md` и напишите: «Прочитай прикреплённую инструкцию Solar Return и используй её в этом разговоре; сначала объясни доступный способ расчёта». Если формат не принимается, скопируйте сам текст.
4. Для проверки без личных данных спросите: «Как ты будешь работать, если у тебя нет Python? Что сделаешь, если я изменю время рождения?» Правильный ответ — браузерный калькулятор/импорт, затем повторный расчёт после изменения, без выдуманных чисел.
5. Если хотите пользоваться постоянно:
   - **ChatGPT:** вставьте `chatgpt.md` в инструкции личного Project. Skills/Plugins требуют своего доступного пути установки.
   - **Claude:** в поддерживаемом интерфейсе загрузите **внутренний `solar-return.zip`** через Customize → Skills и включите навык/выполнение кода. `claude.md` остаётся вариантом без установки.
   - **Grok:** при доступном Skill Creator попросите сохранить `grok.md` как общую инструкцию Solar Return, без личных данных. Проверьте сохранение.
   - **Gemini:** при доступном Skills используйте Create manually и текст `gemini.md`; если у вас ещё Gems, вставьте текст в инструкции Gem. Простой разговор работает без этого шага.
   - **Другой агент:** используйте `any-agent.md` в разговоре или поддерживаемых персональных инструкциях. Локальные Agent Skills-хосты используют папку из внутреннего `solar-return.zip` и свою Python-среду.

**Чтение ≠ подключение ≠ вычисление.** Этот набор не устанавливает всё автоматически. Загрузка в чат/сохранение инструкций не гарантирует запуска Python и `pyswisseph`. Сохранение в одном клиенте не подтверждает установку в другом. Текущие способы и официальные источники: [PLATFORMS.md](https://github.com/tvildanov/solar-return-skill/blob/main/PLATFORMS.md).

### Если Python недоступен

Откройте [браузерный калькулятор](https://tvildanov.github.io/solar-return-skill/), заполните подтверждённые поля, нажмите «Рассчитать», затем «Скопировать запрос для любого ИИ» и вставьте результат в тот же разговор. Можно скачать Markdown-отчёт. Без интернета для браузера и без локальной среды доступно только обсуждение/разбор уже имеющегося результата.

В чате можно исправлять время, место и другие вводные. После исправления нужен новый расчёт или новый экспорт. Неизвестное время нельзя молча заменить полуднем. Условные времена и ректификация остаются гипотезами; событийный рейтинг требует Python-скрипта `rectify.py`, его нет в браузерной форме.

### Приватность и границы

Вычисление в браузере происходит на вашем устройстве; страница загружает ресурсы, а поиск города передаёт его название в Open-Meteo. Вставка/загрузка отчёта передаёт содержимое выбранному AI-сервису. Не добавляйте личные данные в распространяемый набор, общий Skill/Project/Gem или GitHub. Дневник и события жизни необязательны. Астрология не является научно подтверждённым прогнозом и не заменяет медицинские, юридические или финансовые решения.

## English quick start

1. Extract `solar-return-assistant-kit.zip`. Choose `chatgpt.md`, `claude.md`, `grok.md`, `gemini.md`, or `any-agent.md`.
2. Paste the **complete file text** into a new chat, or attach the file and explicitly ask the assistant to use it. The instructions tell it to reply in your language. You do not need to share birth data just to set it up.
3. Optional persistence: use a private ChatGPT Project, a supported Claude Skill upload (`solar-return.zip` inside the kit), Grok Skill Creator, or Gemini Skills/Gems if available in your account. Confirm that saving actually succeeded. See the [platform guide](https://github.com/tvildanov/solar-return-skill/blob/main/PLATFORMS.md) for details.
4. No suitable Python runtime? Use the [browser calculator](https://tvildanov.github.io/solar-return-skill/), choose **Calculate → Copy prompt for any AI**, then paste the result into the same conversation. A saved prompt or uploaded ZIP is not proof that the calculator ran.
5. Ask follow-up questions in chat. Changing birth time, location, year or house system requires a new calculation. Uncertain birth times remain explicit scenarios. Event-based rectification is an optional, unvalidated hypothesis, not a way to establish the true birth minute; its ranking tool requires Python.

The browser loads application resources and city lookup sends the city name to Open-Meteo. Your AI provider receives whatever you paste or upload. Keep personal data out of shared instructions and public repositories. No medical, legal or financial predictions or advice.

## Состав / Contents

- Five standalone `.md` conversation adapters; they do not contain personal data or a second calculator.
- `solar-return.zip`: canonical Agent Skill with Python scripts and dependency list. Dependencies are installed separately only where permitted.
- `LICENSE`: GNU AGPL v3. Author: [AstroEmpathy](https://astroempathy.org).

Reading these files works offline; hosted chats, the public calculator and downloading dependencies may need internet. The package has not been installed in every product/account. These are setup instructions, not a universal one-click installer.

[Repository](https://github.com/tvildanov/solar-return-skill) · [Start guide](https://github.com/tvildanov/solar-return-skill/blob/main/START.md) · [Accuracy and limitations](https://github.com/tvildanov/solar-return-skill/blob/main/ACCURACY.md).
