import typer
import asyncio
from core.engine import G4FEngine
from rich.markdown import Markdown
from rich.console import Console

app = typer.Typer(help='GPT4FREE Terminal Client')
engine = G4FEngine()
console = Console()

async def stream_response(model: str, message: str) -> None:
    '''Асинхронная функция для вывода стрима и подсветки синтаксиса'''
    try:
        full_text = ''
        async for chunk in engine.get_chat_stream(model, message):
            print(chunk, end="", flush=True)
            full_text += chunk
        print()

        md = Markdown(full_text)
        console.print(md)

    except Exception as e:
        typer.echo(f"\n[Ошибка генерации]: {e}", err=True)

@app.command()
def main(
        prompt: str = typer.Option(None, '--prompt', '-p', help='Текст запроса к нейросети'),
        model: str = typer.Option('gpt-4o', '--model', '-m', help='Имя модели (по умолчанию: gpt-4o)')
) -> None:
    if prompt:
        typer.echo(f"Запрос к модели {model}...")
        asyncio.run(stream_response(model, prompt))
    else:
        typer.echo(f"tui")

if __name__ == '__main__':
    app()