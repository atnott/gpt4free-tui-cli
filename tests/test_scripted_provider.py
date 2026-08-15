import pytest

from gpt4free_tui_cli.testing.scripted_provider import ScriptedProvider


@pytest.mark.asyncio
async def test_scripted_provider_is_deterministic_and_records_request() -> None:
    provider = ScriptedProvider(("Привет", " мир"))

    chunks = [
        chunk
        async for chunk in provider.get_chat_stream(
            model="offline-model",
            messages=[{"role": "user", "content": "Тест"}],
            provider="offline",
        )
    ]

    assert chunks == ["Привет", " мир"]
    assert provider.requests == [
        {
            "model": "offline-model",
            "message": None,
            "messages": [{"role": "user", "content": "Тест"}],
            "provider": "offline",
            "web_search": False,
        }
    ]
