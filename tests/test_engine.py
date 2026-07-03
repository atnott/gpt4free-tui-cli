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