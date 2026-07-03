import json
from typing import Any
from core.tools.base import StreamEvent

async def process_chat_stream(app: Any, chat_log: Any, prompt: str) -> None:
    """
    Обрабатывает отправку запроса пользователя, собирает контекст,
    стримит ответ модели и управляет вызовами инструментов.
    """
    chat_id = app.current_chat_id
    history_rows = app.db.get_all_chat_messages(chat_id)

    dialogue_rows = [
        row for row in history_rows
        if row["role"] in ("user", "assistant") and row["content"]
    ]
    messages_context = [
        {"role": row["role"], "content": row["content"]}
        for row in dialogue_rows[-app.MAX_CONTEXT:]
    ]
    messages_context.append({"role": "user", "content": prompt})

    app.db.save_message(chat_id, "user", prompt)
    chat_log.append_message(prompt, is_user=True)
    
    bot_msg = chat_log.append_message("", is_user=False)
    chat_log.scroll_end(animate=False)

    bot_response = ""
    pending_tool_call: dict | None = None

    try:
        async for evt in app.engine.get_chat_stream_with_tools(
            model=app.model,
            messages=messages_context,
            provider=app.provider,
            registry=app.tool_registry,
        ):
            bot_msg.stop_loading()

            if evt.type == "content":
                bot_response += evt.text
                bot_msg.update_content(bot_response)

            elif evt.type == "tool_call":
                pending_tool_call = {"name": evt.tool_name, "arguments": evt.tool_args}
                bot_msg.update_content(bot_response + f"\n\nВызываю `{evt.tool_name}`...")

            elif evt.type == "tool_result":
                if pending_tool_call is not None:
                    pending_tool_call["result"] = evt.tool_result
                    app.db.save_message(
                        chat_id, "tool_call", content=None,
                        tool_calls=json.dumps(pending_tool_call, ensure_ascii=False),
                    )
                    pending_tool_call = None
                bot_msg.update_content(bot_response + f"\n\n`{evt.tool_name}` выполнен, формирую ответ...")

            elif evt.type == "error":
                bot_response += f"\n\n{evt.text}"
                bot_msg.update_content(bot_response)

            chat_log.scroll_end(animate=False)

        bot_msg.update_content(bot_response)
        app.db.save_message(chat_id, "assistant", bot_response)

    except Exception as e:
        bot_msg.stop_loading()
        bot_response = f"Ошибка: {e}"
        bot_msg.update_content(bot_response)
        app.db.save_message(chat_id, "assistant", bot_response)