import json


def test_load_config_creates_defaults(config_manager) -> None:
    assert config_manager.load_config() == config_manager.default_config
    assert config_manager.config_path.exists()


def test_update_config_preserves_other_values(config_manager) -> None:
    config_manager.update_config(last_model="test-model")
    config_manager.update_config(current_chat_id=7)

    assert config_manager.load_config() == {
        "last_model": "test-model",
        "last_provider": None,
        "current_chat_id": 7,
    }


def test_config_is_utf8_json(config_manager) -> None:
    config_manager.update_config(last_model="тест-модель")

    with config_manager.config_path.open(encoding="utf-8") as file:
        assert json.load(file)["last_model"] == "тест-модель"
