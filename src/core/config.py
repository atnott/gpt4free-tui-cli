import json
from pathlib import Path
from typing import Any

class ConfigManager:
    '''Класс для управления сохранением настроек пользователя'''
    def __init__(self, filename: str = 'config.json') -> None:
        self.config_dir = Path.home() / '.config' / 'gpt4free-tui-cli'
        self.config_path = self.config_dir / filename

        self.default_config: dict[str, Any] = {
            'last_model': 'gpt-4o',
            'last_provider': None,
            'current_chat_id': 1
        }

    def _ensure_config_exists(self) -> None:
        '''проверяет наличие папки и файла, если их нет - создает с дефолтными настройками'''
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, indent=4, ensure_ascii=False)

    def load_config(self) -> dict[str, Any]:
        '''Читает конфиг с диска. Если файла нет, сначала создает его'''
        self._ensure_config_exists()
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_config(self, **kwargs: Any) -> None:
        '''Перезаписывает настройки в файле'''
        self._ensure_config_exists()
        current_config = self.load_config()

        current_config.update(kwargs)

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)