import asyncio
from dataclasses import dataclass
from g4f.client import AsyncClient
from g4f.Provider import __providers__

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
            self, model: str, message: str, provider: str | None = None, web_search: bool = False
    ) -> str:
        '''Отправляет запрос к модели'''
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            provider=provider,
            web_search=web_search
        )
        return str(response.choices[0].message.content)

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
            self, model: str, message: str, provider: str | None = None, web_search: bool = False
    ):
        '''Асинхронно стримит кусочки ответа от модели'''
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
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