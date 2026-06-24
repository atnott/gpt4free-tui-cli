import pytest
from typing import AsyncGenerator, List
from g4f_app.domain.models import Message, ProviderStatus
from g4f_app.domain.ports import LLMProviderPort
from g4f_app.domain.services import ChatService

class FakeLLMProvider(LLMProviderPort):
    async def stream_chat(self, messages: List[Message], model: str, provider: str) -> AsyncGenerator[str, None]:
        chunks = ["Привет", " от", " ИИ"]
        for chunk in chunks:
            yield chunk

    async def get_provider_status(self) -> List[ProviderStatus]:
        return []

@pytest.mark.asyncio
async def test_services():
    fake_provider = FakeLLMProvider()
    service = ChatService(fake_provider)

    result = ''
    async for chunk in service.ask_question(text='Привет!', model='test', provider='test'):
        result += chunk

    assert len(service.history) == 2
    assert result == 'Привет от ИИ'
    assert service.llm_provider == fake_provider

