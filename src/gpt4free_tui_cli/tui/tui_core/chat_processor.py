from typing import Any

from gpt4free_tui_cli.application.chat_service import SendMessage
from gpt4free_tui_cli.domain.events import Failed, TextDelta


async def process_chat_stream(app: Any, chat_log: Any, prompt: str) -> None:
    """
    Обрабатывает отправку запроса пользователя, собирает контекст,
    стримит обычный текстовый ответ модели.
    """
    chat_id = app.current_chat_id
    chat_log.append_message(prompt, is_user=True)

    bot_msg = chat_log.append_message("", is_user=False)
    chat_log.scroll_end(animate=False)

    bot_response = ""
    failed = False
    async for event in app.chat_service.send(
        SendMessage(
            chat_id=chat_id, prompt=prompt, model=app.model, provider=app.provider
        )
    ):
        if isinstance(event, TextDelta):
            bot_msg.stop_loading()
            bot_response += event.text
            bot_msg.update_content(bot_response)
            chat_log.scroll_end(animate=False)
        elif isinstance(event, Failed):
            failed = True
            bot_msg.stop_loading()
            bot_msg.update_content(f"Ошибка: {event.message}")
    if not failed:
        bot_msg.stop_loading()
        bot_msg.update_content(bot_response)
