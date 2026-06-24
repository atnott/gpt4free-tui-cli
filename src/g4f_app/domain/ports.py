from typing import Protocol, AsyncGenerator, List
from src.g4f_app.domain.models import Message, ProviderStatus

class LLMProviderPort(Protocol):
    async def stream_chat(
            self, messages: List[Message], model: str, provider: str
    ) -> AsyncGenerator[str, None]:
        ...

    async def get_provider_status(self) -> List[ProviderStatus]:
        ...

class ConfigRepositoryPort(Protocol):
    def load(self) -> dict:
        ...

    def save(self, config: dict) -> None:
        ...