def test_database_creates_default_chat(database_manager) -> None:
    chats = database_manager.get_all_chats()

    assert len(chats) == 1
    assert chats[0]["title"] == "Основной диалог"


def test_database_chat_message_crud(database_manager) -> None:
    chat_id = database_manager.create_chat("Проверка")
    database_manager.update_chat_title(chat_id, "Переименован")
    database_manager.save_message(chat_id, "user", "Вопрос")
    database_manager.save_message(chat_id, "assistant", "Ответ")

    assert database_manager.get_all_chats()[0]["title"] == "Переименован"
    assert [dict(row) for row in database_manager.get_chat_history(chat_id)] == [
        {"role": "user", "content": "Вопрос"},
        {"role": "assistant", "content": "Ответ"},
    ]

    database_manager.delete_chat(chat_id)
    assert database_manager.get_all_chat_messages(chat_id) == []
