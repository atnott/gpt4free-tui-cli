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
            self, model: str, message: str, provider: str | None = None
    ) -> str:
        '''Отправляет запрос к модели'''
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            provider=provider,
            web_search=False
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


if __name__ == '__main__':
    asyncio.run(main())