from typing import List, AsyncGenerator
from g4f_app.domain.models import Message
from g4f_app.domain.ports import LLMProviderPort

class ChatService:
    def __init__(self, llm_provider: LLMProviderPort):
        self.llm_provider = llm_provider
        self.history: List[Message] = []

    async def ask_question(self, text: str, model: str, provider: str) -> AsyncGenerator[str, None]:
        self.history.append(Message(role='user', content=text))
        full_response = ''
        async for chunk in self.llm_provider.stream_chat(self.history, model, provider):
            full_response += chunk
            yield chunk
        self.history.append(Message(role='assistant', content=full_response))
