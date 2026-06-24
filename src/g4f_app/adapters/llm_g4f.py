from typing import AsyncGenerator, List
from g4f.client import AsyncClient
from g4f_app.domain.models import Message, ProviderStatus
from g4f_app.domain.ports import LLMProviderPort

class G4FAdapter(LLMProviderPort):
    def __init__(self):
        self.client: AsyncClient = AsyncClient()

    async def stream_chat(self, messages: List[Message], model: str, provider: str) -> str:
        formatted_messages = [{'role': m.role, 'content': m.content} for m in messages]
        g4f_provider = provider if provider and provider.lower() != "auto" else None

        response = self.client.chat.completions.create(
            model=model,
            provider=g4f_provider,
            messages=formatted_messages,
            stream=True,
        )
        async for chunk in response:
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content

    async def get_provider_status(self) -> List[ProviderStatus]:
        return []