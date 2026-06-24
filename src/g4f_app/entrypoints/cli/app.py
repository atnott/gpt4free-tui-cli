import asyncio
from pathlib import Path
import sys
import typer

sys.path.append(str(Path(__file__).parent.parent / "src"))
from g4f_app.domain.models import Message

app = typer.Typer()

async def run_chat(prompt: str):
    messages = [Message(
        role="user",
        content=prompt
    )]
    print("request:", messages)
    stub ="Hi! I'm a chatbot. How can I assist you today?"
    for char in stub:
        print(char, end='', flush=True)
        await asyncio.sleep(0.05)
    print()

@app.command()
def chat(
    p: str = typer.Option(
        None,
        "--prompt",
        "-p",
        help="Prompt for model"
    )
):
    if not p:
        raise typer.Exit()

    asyncio.run(run_chat(p))\
    
if __name__ == "__main__":
    app()