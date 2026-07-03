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