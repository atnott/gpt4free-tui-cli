import pytest

from gpt4free_tui_cli.domain.events import Completed, TextDelta
from gpt4free_tui_cli.domain.models import Message, ModelRequest


def test_model_request_is_immutable_and_uses_tuple_messages() -> None:
    request = ModelRequest(
        model="offline-model",
        messages=(Message(role="user", content="Тест"),),
    )

    assert request.messages == (Message(role="user", content="Тест"),)
    assert isinstance(TextDelta("часть"), TextDelta)
    assert isinstance(Completed(), Completed)

    with pytest.raises(AttributeError):
        request.model = "другая модель"  # type: ignore[misc]


@pytest.mark.parametrize("content", ["", "   "])
def test_message_rejects_empty_content(content: str) -> None:
    with pytest.raises(ValueError, match="не может быть пустым"):
        Message(role="user", content=content)
