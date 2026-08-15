from typing import Any


async def process_chat_stream(app: Any, chat_log: Any, prompt: str) -> None:
    """
    Обрабатывает отправку запроса пользователя, собирает контекст,
    стримит обычный текстовый ответ модели.
    """
    chat_id = app.current_chat_id
    history_rows = app.db.get_all_chat_messages(chat_id)

    dialogue_rows = [
        row
        for row in history_rows
        if row["role"] in ("user", "assistant") and row["content"]
    ]
    messages_context = [
        {"role": row["role"], "content": row["content"]}
        for row in dialogue_rows[-app.MAX_CONTEXT :]
    ]
    messages_context.append({"role": "user", "content": prompt})

    app.db.save_message(chat_id, "user", prompt)
    chat_log.append_message(prompt, is_user=True)

    bot_msg = chat_log.append_message("", is_user=False)
    chat_log.scroll_end(animate=False)

    bot_response = ""
    try:
        async for chunk in app.engine.get_chat_stream(
            model=app.model,
            messages=messages_context,
            provider=app.provider,
        ):
            bot_msg.stop_loading()
            bot_response += chunk
            bot_msg.update_content(bot_response)

            chat_log.scroll_end(animate=False)

        bot_msg.update_content(bot_response)
        app.db.save_message(chat_id, "assistant", bot_response)

    except Exception as e:
        bot_msg.stop_loading()
        bot_response = f"Ошибка: {e}"
        bot_msg.update_content(bot_response)
        app.db.save_message(chat_id, "assistant", bot_response)
