import typer
import asyncio
from core.engine import G4FEngine
from rich.markdown import Markdown
from rich.console import Console
from core.config import ConfigManager

app = typer.Typer(help='GPT4FREE Terminal Client')
engine = G4FEngine()
console = Console()
config = ConfigManager()

async def stream_response(model: str, provider: str | None = None, message: str = '') -> None:
    '''Асинхронная функция для вывода стрима и подсветки синтаксиса'''
    try:
        full_text = ''
        async for chunk in engine.get_chat_stream(model=model, provider=provider, message=message):
            print(chunk, end="", flush=True)
            full_text += chunk
        print()

        md = Markdown(full_text)
        console.print(md)

        config.update_config(model=model, provider=provider)

    except Exception as e:
        typer.echo(f'\n[Ошибка генерации]: {e}', err=True)

@app.command()
def main(
        prompt: str = typer.Option(None, '--prompt', '-p', help='Текст запроса к нейросети'),
        model: str = typer.Option(None, '--model', '-m', help='Имя модели (по умолчанию: gpt-4o)'),
        provider: str = typer.Option(None, '--provider', '-pr', help='Имя конкретного провайдера')
) -> None:
    if prompt:
        user_settings = config.load_config()
        chosen_model = model or user_settings.get('last_model', 'gpt-4o')
        chosen_provider = provider or user_settings.get('last_provider', None)

        prov_log = f' через [{chosen_provider}]' if chosen_provider else ' (автовыбор провайдера)'
        typer.echo(f'Запрос к модели [{chosen_model}]{prov_log}...')
        asyncio.run(stream_response(chosen_model, chosen_provider, prompt))
    else:
        typer.echo(f'tui')

if __name__ == '__main__':
    app()