import typer
import asyncio
from rich.markdown import Markdown
from rich.console import Console
from rich.table import Table
from rich.live import Live
from gpt4free_tui_cli import __version__
from gpt4free_tui_cli.bootstrap import (
    ApplicationDependencies,
    create_application_dependencies,
    create_engine,
)
from gpt4free_tui_cli.tui.app import G4FreeTUI

app = typer.Typer(help="GPT4FREE Terminal Client")
console = Console()


def _show_version(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_show_version,
        is_eager=True,
        help="Показать версию и выйти.",
    ),
) -> None:
    """GPT4FREE Terminal Client."""


async def stream_response(
    model: str,
    dependencies: ApplicationDependencies,
    provider: str | None = None,
    message: str | None = None,
    messages: list[dict] | None = None,
    web_search: bool = False,
    chat_id: int = 1,
) -> None:
    """Асинхронная функция для вывода стрима и подсветки синтаксиса"""
    try:
        full_text = ""
        with Live(
            Markdown(full_text),
            console=console,
            refresh_per_second=15,
            vertical_overflow="visible",
        ) as live:
            async for chunk in dependencies.engine.get_chat_stream(
                model=model,
                provider=provider,
                message=message,
                messages=messages,
                web_search=web_search,
            ):
                for char in chunk:
                    full_text += char
                    live.update(Markdown(full_text))

                    await asyncio.sleep(0.003)

        dependencies.config.update_config(last_model=model, last_provider=provider)

        if full_text.strip():
            dependencies.db.save_message(
                chat_id=chat_id, role="assistant", content=full_text
            )

    except Exception as e:
        typer.echo(f"\n[Ошибка генерации]: {e}", err=True)


@app.command()
def main(
    prompt: str = typer.Option(
        None, "--prompt", "-p", help="Текст запроса к нейросети"
    ),
    model: str = typer.Option(
        None, "--model", "-m", help="Имя модели (по умолчанию: gpt-4o)"
    ),
    provider: str = typer.Option(
        None, "--provider", "-pr", help="Имя конкретного провайдера"
    ),
    web: bool = typer.Option(False, "--web", "-w", help="Включить поиск в интернете"),
    chat_id: int = typer.Option(None, "--id", "-i", help="Идентификатор сессии чата"),
) -> None:
    if prompt:
        dependencies = create_application_dependencies()
        user_settings = dependencies.config.load_config()
        chosen_model = model or user_settings.get("last_model", "gpt-4o")
        chosen_provider = provider or user_settings.get("last_provider", None)
        active_chat_id = chat_id or user_settings.get("current_chat_id", 1)

        prov_log = (
            f" через [{chosen_provider}]"
            if chosen_provider
            else " (автовыбор провайдера)"
        )
        web_log = " [с поиском в сети]" if web else ""

        typer.echo(
            f"Запрос к модели [{chosen_model}]{prov_log}{web_log} в чат [ID: {active_chat_id}]..."
        )

        dependencies.db.save_message(
            chat_id=active_chat_id, role="user", content=prompt
        )
        history_rows = dependencies.db.get_chat_history(chat_id=active_chat_id)
        formatted_messages = [
            {"role": row["role"], "content": row["content"]} for row in history_rows
        ]

        asyncio.run(
            stream_response(
                model=chosen_model,
                dependencies=dependencies,
                provider=chosen_provider,
                message=None,
                messages=formatted_messages,
                web_search=web,
                chat_id=active_chat_id,
            )
        )
    else:
        G4FreeTUI(create_application_dependencies()).run()


@app.command(name="models")
def list_models() -> None:
    """Вывести список всех уникальных моделей от работающих провайдеров"""
    models = create_engine().get_all_models()

    table = Table(title=f"Доступно моделей: {len(models)}шт")
    table.add_column("Имя модели (-m)")

    for model in models:
        table.add_row(model)
    console.print(table)


@app.command(name="providers")
def list_providers() -> None:
    """Вывести список всех работающих провайдеров и их моделей"""
    providers_status = create_engine().get_available_providers()

    table = Table(
        title=f"Работающие провайдеры ({len(providers_status)}шт)", show_lines=True
    )
    table.add_column("Провайдер (-pr)")
    table.add_column("Поддерживаемые модели")

    for provider in providers_status:
        models_str = ", ".join(provider.supported_models)
        table.add_row(provider.name, models_str)

    console.print(table)


@app.command(name="chats")
def list_chats() -> None:
    """Вывести список всех существующих чатов"""
    dependencies = create_application_dependencies()
    chats_list = dependencies.db.get_all_chats()

    if not chats_list:
        console.print("У вас пока нет созданных чатов!")
        return

    user_settings = dependencies.config.load_config()
    active_chat_id = user_settings.get("current_chat_id", 1)

    table = Table(title=f"Ваши диалоги ({len(chats_list)}шт)")
    table.add_column("id чата")
    table.add_column("Название диалога")
    table.add_column("Дата создания")

    for chat in chats_list:
        is_active = chat["id"] == active_chat_id

        row_style = "bold green on #1a1a1a" if is_active else ""

        table.add_row(
            str(chat["id"]), chat["title"], chat["created_at"], style=row_style
        )

    console.print(table)


@app.command(name="new-chat")
def create_new_chat(
    title: str = typer.Argument(
        "Название по умолчанию", help="Название для нового чата"
    ),
) -> None:
    """Создать новую сессию чата"""
    dependencies = create_application_dependencies()
    new_id = dependencies.db.create_chat(title=title)
    dependencies.config.update_config(current_chat_id=new_id)
    console.print(f"Чат `{title}` c id: {new_id} успешно создан!")


@app.command(name="select-chat")
def select_chat(chat_id: int = typer.Argument(1, help="id необходимого чата")) -> None:
    """Переключиться на указанный чат"""
    dependencies = create_application_dependencies()
    all_chats = dependencies.db.get_all_chats()
    existing_ids = [chat["id"] for chat in all_chats]
    if chat_id not in existing_ids:
        console.print(f"Ошибка: Чата с id {chat_id} не существует!")
        return
    dependencies.config.update_config(current_chat_id=chat_id)
    console.print(f"Успешно переключено на чат id: {chat_id}")


if __name__ == "__main__":
    app()
