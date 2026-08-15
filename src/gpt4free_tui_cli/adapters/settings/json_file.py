"""Переходный adapter существующего JSON config manager."""

from gpt4free_tui_cli.core.config import ConfigManager


class JsonSettings:
    def __init__(self, config: ConfigManager) -> None:
        self._config = config

    def save_last_selection(self, *, model: str, provider: str | None) -> None:
        self._config.update_config(last_model=model, last_provider=provider)
