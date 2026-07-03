import json
import asyncio
from dataclasses import dataclass
from g4f.client import AsyncClient
from g4f.Provider import __providers__
from core.tools.base import ToolRegistry, ToolExecutor, StreamEvent
from core.tools.prompting import build_tools_system_prompt, extract_tool_call, is_safe_to_stream

MAX_TOOL_ITERATIONS = 5


@dataclass
class ProviderStatus():
    name: str
    is_working: bool
    supported_models: list[str]


class G4FEngine:
    '''Главный класс, отвечающий за прямое взаимодействие с API g4f'''

    def __init__(self) -> None:
        self.client = AsyncClient()

    async def get_chat_response(
            self,
            model: str,
            message: str | None = None,
            messages: list[dict] | None = None,
            provider: str | None = None,
            web_search: bool = False
    ) -> str:
        '''Отправляет запрос к модели'''
        formatted_messages = messages if messages is not None else [{'role': 'user', 'content': message}]
        response = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            provider=provider,
            web_search=web_search
        )
        return str(response.choices[0].message.content)

    async def get_chat_stream_with_tools(
            self,
            model: str,
            messages: list[dict],
            registry: ToolRegistry,
            provider: str | None = None,
    ):
        '''Агентный стрим с tool calling'''
        executor = ToolExecutor(registry)
        working_messages = list(messages)

        tools_prompt = build_tools_system_prompt(registry)
        if tools_prompt:
            working_messages = [{"role": "system", "content": tools_prompt}] + working_messages

        for _ in range(MAX_TOOL_ITERATIONS):
            buffer = ""
            emitted_len = 0

            response = self.client.chat.completions.create(
                model=model,
                messages=working_messages,
                provider=provider,
                stream=True,
            )

            async for chunk in response:
                try:
                    content = chunk.choices[0].delta.content or ""
                except AttributeError:
                    content = ""
                if not content:
                    continue

                buffer += content

                if is_safe_to_stream(buffer):
                    new_text = buffer[emitted_len:]
                    if new_text:
                        yield StreamEvent(type="content", text=new_text)
                        emitted_len = len(buffer)

            tool_call_dict = extract_tool_call(buffer)

            if not tool_call_dict:
                remainder = buffer[emitted_len:]
                if remainder:
                    yield StreamEvent(type="content", text=remainder)
                return

            name = tool_call_dict["function"]["name"]
            args = json.loads(tool_call_dict["function"]["arguments"] or "{}")
            yield StreamEvent(type="tool_call", tool_name=name, tool_args=args)

            tool_result = await executor.execute(tool_call_dict)
            yield StreamEvent(type="tool_result", tool_name=name, tool_result=tool_result["content"])

            working_messages.append({"role": "assistant", "content": buffer})
            working_messages.append({
                "role": "user",
                "content": f"Результат вызова {name}: {tool_result['content']}\n\nПродолжи ответ на основе этого результата."
            })

        yield StreamEvent(type="error", text="Превышен лимит итераций вызова инструментов")

    def get_available_providers(self) -> list[ProviderStatus]:
        '''Собирает актуальный список работающих провайдеров и их моделей'''
        active_providers: list[ProviderStatus] = []
        for provider in __providers__:
            is_working = getattr(provider, "working", False)
            models = getattr(provider, "models", [])

            if is_working and models:
                models_list = [str(m) for m in models]
                active_providers.append(
                    ProviderStatus(
                        name=provider.__name__,
                        is_working=is_working,
                        supported_models=models_list,
                    )
                )
        return active_providers

    def get_all_models(self) -> list[str]:
        '''Возвращает отсортированный список всех уникальных моделей от работающих провайдеров'''
        unique_models: set[str] = set()
        for provider in self.get_available_providers():
            unique_models.update(provider.supported_models)

        return sorted(unique_models)

    async def get_chat_stream(
            self,
            model: str,
            message: str | None = None,
            messages: list[dict] | None = None,
            provider: str | None = None,
            web_search: bool = False
    ):
        '''Асинхронно стримит кусочки ответа от модели (без tool calling)'''
        formatted_messages = messages if messages is not None else [{'role': 'user', 'content': message}]
        response = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            provider=provider,
            stream=True,
            web_search=web_search,
        )

        async for chunk in response:
            try:
                content = chunk.choices[0].delta.content or ""
            except AttributeError:
                content = str(chunk)

            if content:
                yield str(content)

async def main():
    engine = G4FEngine()
    providers = engine.get_available_providers()
    for provider in providers[:10]:
        print(provider)

    answer = await engine.get_chat_response(
        model='gpt-4o',
        message='Привет, назови столицу России!'
    )
    print(answer)

    answer = engine.get_all_models()
    print(len(answer))

    async for chunk in engine.get_chat_stream(model='gpt-4o', message='Напиши стих из 4 строк'):
        print(chunk, end="", flush=True)


if __name__ == '__main__':
    asyncio.run(main())