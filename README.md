# GPT4Free TUI & CLI Client

Терминальный клиент над `g4f` с двумя интерфейсами: Typer CLI для одного
запроса и Textual TUI для работы с чатами. Проект находится на учебном
baseline: packaging, offline-проверки и границы зависимостей стабилизированы,
а provider-neutral application layer и надёжное хранение ещё не выделены.

## Возможности

- потоковый текстовый ответ от `g4f`;
- CLI-команды для моделей, провайдеров и чатов;
- Textual TUI с историей диалогов и выбором модели/провайдера;
- SQLite для чатов и сообщений, JSON для последней модели, провайдера и чата;
- Markdown-рендеринг ответов через Rich;
- deterministic `ScriptedProvider` для offline-тестов.

Локальных инструментов и tool calling в приложении нет. Строка вида
`<tool_call>...</tool_call>` считается обычным текстом и не выполняется.

## Установка

Нужен Python 3.12+ и [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/atnott/gpt4free-tui-cli.git
cd gpt4free-tui-cli
uv sync --group dev
```

Если домашний cache `uv` недоступен для записи, используйте отдельный cache:

```bash
UV_CACHE_DIR=/tmp/gpt4free-tui-cli-uv-cache uv sync --group dev
```

## Запуск

Проверить установленную в окружение точку входа:

```bash
uv run g4f-cli --help
uv run g4f-cli --version
```

Открыть интерактивный TUI:

```bash
uv run g4f-cli main
```

Отправить одиночный запрос (это обращается к внешнему `g4f`-провайдеру):

```bash
uv run g4f-cli main --prompt "Объясни async/await в Python"
```

## Команды

| Команда | Назначение | Создаёт SQLite БД |
| --- | --- | --- |
| `g4f-cli --help` | Справка | Нет |
| `g4f-cli --version` | Версия пакета | Нет |
| `g4f-cli models` | Каталог моделей от `g4f` | Нет |
| `g4f-cli providers` | Каталог провайдеров от `g4f` | Нет |
| `g4f-cli chats` | Показать чаты | Да |
| `g4f-cli new-chat "Название"` | Создать и выбрать чат | Да |
| `g4f-cli select-chat 2` | Выбрать существующий чат | Да |
| `g4f-cli main` | Запустить TUI | Да |
| `g4f-cli main -p "..."` | Отправить запрос в чат | Да |

`models` и `providers` используют metadata библиотеки `g4f`. Статус
`provider.working` не является проверкой доступности провайдера.

## Данные и контекст

- Конфигурация: `~/.config/gpt4free-tui-cli/config.json`.
- SQLite: `storage.db` в корне текущего checkout. Это известное временное
  ограничение: при установленной сборке путь пока не перенесён в user data
  directory.
- CLI передаёт в запрос последние 10 сообщений истории.
- TUI передаёт последние 20 непустых сообщений с ролями `user` и `assistant`.

Окно контекста считается по сообщениям, а не по токенам. В проекте пока нет
summary, векторного поиска, профиля пользователя или отдельного memory API.

## Структура

```text
src/gpt4free_tui_cli/
├── bootstrap.py              # единственный composition root
├── core/                     # config, SQLite и конкретный g4f adapter
├── presentation/cli.py       # Typer entry point
├── testing/scripted_provider.py
└── tui/                      # Textual app, screens и widgets
tests/                        # deterministic offline tests
.github/workflows/ci.yml      # quality gates и wheel smoke test
```

`bootstrap.py` создаёт concrete-зависимости для команд, которым они нужны.
Поэтому импорт CLI и read-only команды не инициализируют БД.

## Проверка качества

```bash
UV_CACHE_DIR=/tmp/gpt4free-tui-cli-uv-cache uv lock --check --offline
UV_CACHE_DIR=/tmp/gpt4free-tui-cli-uv-cache uv run ruff check .
UV_CACHE_DIR=/tmp/gpt4free-tui-cli-uv-cache uv run ruff format --check .
UV_CACHE_DIR=/tmp/gpt4free-tui-cli-uv-cache uv run mypy
UV_CACHE_DIR=/tmp/gpt4free-tui-cli-uv-cache uv run pytest -q --cov
UV_CACHE_DIR=/tmp/gpt4free-tui-cli-uv-cache uv build
```

CI также устанавливает собранный wheel в чистый временный virtualenv и
запускает `g4f-cli --help`.

## Текущие ограничения

- CLI и TUI пока реализуют похожий use case раздельно; общий `ChatService`
  появится в следующем архитектурном этапе.
- `g4f` пока импортируется напрямую concrete engine, поэтому провайдер ещё не
  сменяем через отдельный port.
- Нет token budget, суммаризации истории, cancellation/retry policy и
  полноценного покрытия TUI type checking.
- Ошибки сетевого запроса требуют отдельного UX-улучшения: TUI пока может
  сохранять текст ошибки как ответ ассистента.

## Лицензия

Проект распространяется по лицензии [MIT](LICENSE).
