# Установка / Installation

Этот ZIP содержит навык `solar-return` версии 0.4.0 от AstroEmpathy.

1. В Claude откройте **Customize → Skills** и загрузите исходный ZIP целиком.
2. Включите навык и выполнение кода. Доступность зависит от клиента и аккаунта.
3. Напишите: «Рассчитай мой соляр на 2027 год; сначала спроси недостающие данные».

Для Claude Code: после просмотра исходников поместите эту папку в `~/.claude/skills/solar-return`, не перезаписывая старую копию. Для Python используйте отдельную виртуальную среду, затем `python -m pip install -r requirements.txt` и `python scripts/solar_return.py --help` из этой папки. Установка зависимостей скачивает сторонние пакеты; согласуйте её с владельцем среды. Не используйте `sudo pip` / `--break-system-packages`.

Birth data may be processed and retained by the AI host. The calculator makes no network calls, but `--json` saves birth time and coordinates to a local file. Avoid publishing results. This skill uses astrology for reflection, not scientific predictions or professional advice. License: GNU AGPL v3, included in `LICENSE`.

English: upload this ZIP in Claude's **Customize → Skills**, enable the skill and code execution, and ask “Calculate my solar return.” Installation is account/client-dependent. Review source and dependencies before local execution.

Full instructions and source: https://github.com/tvildanov/solar-return-skill
