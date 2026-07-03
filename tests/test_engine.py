import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from core.engine import G4FEngine, ProviderStatus


class TestG4FEngineInitialization:
    """Тесты инициализации движка."""

    def test_engine_creates_async_client(self, mock_g4f_client):
        """Проверка создания AsyncClient при инициализации."""
        engine = G4FEngine()
        assert engine.client is mock_g4f_client

    def test_engine_client_is_async(self, engine):
        """Клиент должен быть асинхронным."""
        assert isinstance(engine.client, AsyncMock)

class TestGetChatResponse:
    """Тесты синхронного (async) получения ответа."""

    @pytest.mark.asyncio
    async def test_get_chat_response_with_message(self, engine, mock_g4f_client):
        """Запрос с одним сообщением."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Ответ модели"))]
        mock_g4f_client.chat.completions.create.return_value = mock_response

        result = await engine.get_chat_response(
            model="gpt-4o",
            message="Привет!"
        )

        mock_g4f_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Привет!"}],
            provider=None,
            web_search=False
        )
        assert result == "Ответ модели"

    @pytest.mark.asyncio
    async def test_get_chat_response_with_messages_list(self, engine, mock_g4f_client):
        """Запрос со списком сообщений (история)."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Контекстный ответ"))]
        mock_g4f_client.chat.completions.create.return_value = mock_response

        messages = [
            {"role": "user", "content": "Вопрос 1"},
            {"role": "assistant", "content": "Ответ 1"},
        ]

        result = await engine.get_chat_response(
            model="gpt-4o",
            messages=messages
        )

        assert result == "Контекстный ответ"
        call_args = mock_g4f_client.chat.completions.create.call_args
        assert call_args.kwargs["messages"] == messages

    @pytest.mark.asyncio
    async def test_get_chat_response_with_provider(self, engine, mock_g4f_client):
        """Запрос с указанием провайдера."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Ответ"))]
        mock_g4f_client.chat.completions.create.return_value = mock_response

        await engine.get_chat_response(
            model="gpt-4o",
            message="Test",
            provider="Bing"
        )

        call_args = mock_g4f_client.chat.completions.create.call_args
        assert call_args.kwargs["provider"] == "Bing"

    @pytest.mark.asyncio
    async def test_get_chat_response_with_web_search(self, engine, mock_g4f_client):
        """Запрос с включённым веб-поиском."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Результат поиска"))]
        mock_g4f_client.chat.completions.create.return_value = mock_response

        await engine.get_chat_response(
            model="gpt-4o",
            message="Новости",
            web_search=True
        )

        call_args = mock_g4f_client.chat.completions.create.call_args
        assert call_args.kwargs["web_search"] is True

    @pytest.mark.asyncio
    async def test_get_chat_response_error_handling(self, engine, mock_g4f_client):
        """Обработка ошибок API."""
        mock_g4f_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            await engine.get_chat_response(model="gpt-4o", message="Test")

    @pytest.mark.asyncio
    async def test_get_chat_response_empty_content(self, engine, mock_g4f_client):
        """Обработка пустого ответа."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=""))]
        mock_g4f_client.chat.completions.create.return_value = mock_response

        result = await engine.get_chat_response(model="gpt-4o", message="Test")
        assert result == ""

class TestGetAvailableProviders:
    """Тесты получения списка провайдеров."""

    def test_get_available_providers_filters_working(self, engine):
        """Фильтрация только работающих провайдеров."""
        mock_provider1 = MagicMock()
        mock_provider1.working = True
        mock_provider1.models = ["gpt-4o", "claude-3"]
        mock_provider1.__name__ = "ProviderA"

        mock_provider2 = MagicMock()
        mock_provider2.working = False
        mock_provider2.models = ["gpt-4o"]
        mock_provider2.__name__ = "ProviderB"

        mock_provider3 = MagicMock()
        mock_provider3.working = True
        mock_provider3.models = []
        mock_provider3.__name__ = "ProviderC"

        with patch("core.engine.__providers__", [mock_provider1, mock_provider2, mock_provider3]):
            providers = engine.get_available_providers()

            assert len(providers) == 1
            assert providers[0].name == "ProviderA"
            assert providers[0].is_working is True
            assert providers[0].supported_models == ["gpt-4o", "claude-3"]

    def test_get_available_providers_no_models(self, engine):
        """Провайдеры без моделей исключаются."""
        mock_provider = MagicMock()
        mock_provider.working = True
        mock_provider.models = []
        mock_provider.__name__ = "EmptyProvider"

        with patch("core.engine.__providers__", [mock_provider]):
            providers = engine.get_available_providers()
            assert len(providers) == 0

    def test_get_available_providers_models_conversion(self, engine):
        """Проверка конвертации моделей в строки."""
        mock_provider = MagicMock()
        mock_provider.working = True
        mock_provider.models = [MagicMock(__str__=lambda self: "model-1")]
        mock_provider.__name__ = "TestProvider"

        with patch("core.engine.__providers__", [mock_provider]):
            providers = engine.get_available_providers()
            assert providers[0].supported_models == ["model-1"]

    def test_get_available_providers_empty_list(self, engine):
        """Пустой список провайдеров."""
        with patch("core.engine.__providers__", []):
            providers = engine.get_available_providers()
            assert providers == []

class TestGetAllModels:
    """Тесты получения списка всех моделей."""

    def test_get_all_models_unique_and_sorted(self, engine):
        """Проверка уникальности и сортировки моделей."""
        mock_provider1 = MagicMock()
        mock_provider1.working = True
        mock_provider1.models = ["gpt-4o", "claude-3"]
        mock_provider1.__name__ = "P1"

        mock_provider2 = MagicMock()
        mock_provider2.working = True
        mock_provider2.models = ["gpt-4o", "llama-3"]
        mock_provider2.__name__ = "P2"

        with patch("core.engine.__providers__", [mock_provider1, mock_provider2]):
            models = engine.get_all_models()

            assert models == ["claude-3", "gpt-4o", "llama-3"]
            assert len(models) == 3  # уникальные

    def test_get_all_models_empty(self, engine):
        """Пустой список моделей."""
        with patch("core.engine.__providers__", []):
            models = engine.get_all_models()
            assert models == []

class TestGetChatStream:
    """Тесты стримингового получения ответа."""

    @pytest.mark.asyncio
    async def test_get_chat_stream_basic(self, engine, mock_g4f_client):
        """Базовый стриминг."""
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock(delta=MagicMock(content="Привет"))]
        chunk2 = MagicMock()
        chunk2.choices = [MagicMock(delta=MagicMock(content=" мир"))]

        async def async_generator():
            yield chunk1
            yield chunk2

        mock_g4f_client.chat.completions.create.return_value = async_generator()

        result = []
        async for chunk in engine.get_chat_stream(model="gpt-4o", message="Test"):
            result.append(chunk)

        assert result == ["Привет", " мир"]

    @pytest.mark.asyncio
    async def test_get_chat_stream_with_messages(self, engine, mock_g4f_client):
        """Стриминг с историей сообщений."""
        chunk = MagicMock()
        chunk.choices = [MagicMock(delta=MagicMock(content="Ответ"))]

        async def async_generator():
            yield chunk

        mock_g4f_client.chat.completions.create.return_value = async_generator()

        messages = [{"role": "user", "content": "Вопрос"}]
        result = []
        async for chunk in engine.get_chat_stream(model="gpt-4o", messages=messages):
            result.append(chunk)

        call_args = mock_g4f_client.chat.completions.create.call_args
        assert call_args.kwargs["messages"] == messages
        assert call_args.kwargs["stream"] is True

    @pytest.mark.asyncio
    async def test_get_chat_stream_empty_chunks(self, engine, mock_g4f_client):
        """Пропуск пустых чанков."""
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock(delta=MagicMock(content=""))]
        chunk2 = MagicMock()
        chunk2.choices = [MagicMock(delta=MagicMock(content="Текст"))]

        async def async_generator():
            yield chunk1
            yield chunk2

        mock_g4f_client.chat.completions.create.return_value = async_generator()

        result = []
        async for chunk in engine.get_chat_stream(model="gpt-4o", message="Test"):
            result.append(chunk)

        assert result == ["Текст"]

    @pytest.mark.asyncio
    async def test_get_chat_stream_attribute_error(self, engine, mock_g4f_client):
        """Обработка AttributeError (нет choices/delta)."""
        chunk = MagicMock()
        # choices отсутствует, вызовет AttributeError
        del chunk.choices

        async def async_generator():
            yield chunk

        mock_g4f_client.chat.completions.create.return_value = async_generator()

        result = []
        async for chunk in engine.get_chat_stream(model="gpt-4o", message="Test"):
            result.append(chunk)

        # Должен вернуть str(chunk) при AttributeError
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_chat_stream_with_provider_and_web_search(self, engine, mock_g4f_client):
        """Стриминг с провайдером и веб-поиском."""
        chunk = MagicMock()
        chunk.choices = [MagicMock(delta=MagicMock(content="OK"))]

        async def async_generator():
            yield chunk

        mock_g4f_client.chat.completions.create.return_value = async_generator()

        result = []
        async for chunk in engine.get_chat_stream(
            model="gpt-4o",
            message="Test",
            provider="Bing",
            web_search=True
        ):
            result.append(chunk)

        call_args = mock_g4f_client.chat.completions.create.call_args
        assert call_args.kwargs["provider"] == "Bing"
        assert call_args.kwargs["web_search"] is True
        assert call_args.kwargs["stream"] is True
