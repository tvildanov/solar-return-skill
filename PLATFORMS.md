# ChatGPT, Codex, Cursor, Claude и другие агенты

Документация платформ сверена **30 октября 2026**. **Публичная ссылка даёт доступ к файлам, но не устанавливает навык, не предоставляет Python и не выдаёт разрешение на запуск.** Одна ссылка для распространения: https://github.com/tvildanov/solar-return-skill . Начните с [готового запроса](START.md).

| Среда | Что подготовлено | Что ещё требуется |
|---|---|---|
| Claude с Skills | `solar-return.zip` | Загрузка/включение навыка и выполнение кода |
| Codex CLI / IDE / подходящая локальная среда ChatGPT desktop | Стандартная папка навыка, безопасный копировщик | Доступ к выбранной папке, обнаружение навыка, Python |
| Cursor | Папка навыка, portable plugin и каталог репозитория | Разрешённый локальный/GitHub импорт, установка, Python |
| ChatGPT workspace с импортом плагинов | Portable plugin + `.agents/plugins/marketplace.json` | Workspace admin, разрешённый импорт, установка для пользователя и доступная среда выполнения |
| Обычный ChatGPT / другой чат | Читаемые инструкции и стартовый запрос | Чтение файлов не означает постоянную установку; вычисление возможно только при реальных инструментах |
| Произвольный агент с Python | Тот же CLI и JSON | Python 3.9+, зависимости, разрешение на выполнение |

**Проверено здесь:** содержимое пакетов, официальный формат manifest, тестовые копирования в изолированные каталоги и запуск Python на Linux. **Не проверено:** импорт/активация в каждом настоящем клиенте, аккаунте и ОС. Plugin не опубликован в публичных каталогах OpenAI/Cursor и не предоставляет удалённый API расчёта.

## ChatGPT: не путать чат, навык и плагин

Для одного разговора дайте ассистенту [стартовый запрос](START.md). Если он не может открыть ссылку, приложите скачанные `SKILL.md` и нужные файлы. Если нет Python или нельзя установить зависимость, новый точный расчёт этим способом недоступен. Можно попросить разобрать уже полученный JSON с пометкой «не пересчитывал».

Официальная документация различает standalone skills в desktop/Codex и распространение через plugins. Само наличие ZIP в сообщении не подтверждает ни одно из этих действий. В поддерживаемом ChatGPT интерфейсе установленный навык выбирается через `@`; в Codex CLI/IDE — через `/skills` или `$solar-return`. [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills).

Для повторного использования в ChatGPT workspace администратор может импортировать каталог этого репозитория: **Admin → Plugins → Add → Import marketplace**, Source — URL репозитория, Path — пустой, Ref — проверенный commit или `main`. Затем нужно проверить результат импорта и установить/разрешить plugin. Это действие выполняет администратор в своём workspace; мы не импортировали его за вас. Права, доступность инструментов и политики workspace сохраняются. [OpenAI: GitHub marketplace import](https://learn.chatgpt.com/docs/enterprise/plugin-management).

<a id="local-skill"></a>
## Локальный навык: Codex, Cursor, Claude Code

Сначала скачайте/клонируйте репозиторий, прочитайте исходники. Из корня репозитория можно проверить план без записи:

```bash
python3 tools/install_skill.py --host codex --project /absolute/path/to/project --dry-run
```

После проверки и разрешения выполните ту же команду без `--dry-run`. Вместо `codex` выберите `cursor` или `claude-code`. Для профиля текущего пользователя замените `--project ...` на `--user`.

Копировщик **только переносит шесть разрешённых файлов**. Он не скачивает пакеты, не запускает калькулятор, не меняет настройки клиента, не перезаписывает существующий навык и отклоняет символьные ссылки в целевом пути. Обновление требует отдельного осознанного решения о старой копии.

| `--host` | В проекте | В профиле |
|---|---|---|
| `codex` | `.agents/skills/solar-return` | `~/.agents/skills/solar-return` |
| `cursor` | `.cursor/skills/solar-return` | `~/.cursor/skills/solar-return` |
| `claude-code` | `.claude/skills/solar-return` | `~/.claude/skills/solar-return` |

Если меню не обновилось, перезапустите клиент/перезагрузите skills предусмотренным им способом. В Cursor и Claude Code выберите `/solar-return`. На удалённом worker нужны файлы **его** среды: папка на вашем ноутбуке сама туда не переносится. Синхронизация personal skills, cloud sessions и ограничения организации зависят от конкретного продукта. Источники: [OpenAI discovery](https://learn.chatgpt.com/docs/customization/overview), [Cursor skills](https://cursor.com/docs/skills), [Claude Code skills](https://code.claude.com/docs/en/skills).

Python-среда создаётся **отдельно**, после согласования:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r solar-return/requirements.txt
.venv/bin/python solar-return/scripts/solar_return.py --help
```

Команды выше — POSIX (Linux/macOS), не обещание проверки каждой ОС. Укажите агенту абсолютный путь к этому интерпретатору; не заставляйте его устанавливать пакеты повторно. Для Python 3.12+ зависимость может собираться из исходников и требовать компилятор. Блокировка установки — причина сообщить ограничение, не использовать `sudo pip` или обход защиты.

<a id="plugins"></a>
## Portable plugin и каталоги

`plugins/solar-return/plugin.json` следует **Agent Plugins 1.0**; `skills/solar-return/` содержит побайтную копию канонического навыка. В пакете нет MCP-сервера, hooks, автоматического инсталлятора зависимостей или секретов. [OpenAI package format](https://developers.openai.com/plugins/build/plugins), [Cursor supported formats](https://cursor.com/docs/reference/plugins).

- **Cursor GitHub import:** в поддерживаемом интерфейсе Customize используйте **From GitHub Repository** и URL этого репозитория; `.cursor-plugin/marketplace.json` описывает единственный plugin. Затем установите его и проверьте появление навыка. Администратор может запретить импорт. Альтернатива — разрешённый локальный импорт папки `plugins/solar-return`; не импортируйте вместо неё обычный skill ZIP. [Cursor repository installation](https://cursor.com/docs/skills).
- **Codex local marketplace:** репозиторий содержит `.agents/plugins/marketplace.json`. Поддерживаемая CLI-команда `codex plugin marketplace add tvildanov/solar-return-skill --ref main` добавляет источник, **не доказывает установку/исполнение**. Для установки и проверки следуйте интерфейсу desktop и правилам своего аккаунта. Для воспроизводимости закрепите проверенный commit. [OpenAI local marketplaces](https://developers.openai.com/plugins/build/plugins).
- **ChatGPT workspace import:** см. раздел выше; требуется администратор. Пакет в GitHub — не одобренная запись публичного Plugins Directory. Возможность импортировать, установить и выполнить код проверяется отдельно.

[Скачать plugin ZIP](https://github.com/tvildanov/solar-return-skill/raw/main/solar-return-plugin.zip) · [SHA-256](solar-return-plugin.zip.sha256)

## Проверка результата, а не только установки

Попросите агент сообщить: **(1)** какие файлы прочитаны и какая версия; **(2)** где навык обнаружен/установлен; **(3)** какая Python-среда и версии зависимостей; **(4)** какой реальный запуск завершился успешно. Затем проверьте JSON: 24 интервала, явные зоны/система домов, дата возврата и входные допущения.

Успешные unit tests и сохранение старого результата сами по себе не доказывают независимую астрономическую точность. Читайте [датированный отчёт](VERIFICATION.md) и [независимое сравнение Солнца с JPL](ACCURACY.md). Личные данные и созданный JSON не должны попадать в публичный репозиторий.
