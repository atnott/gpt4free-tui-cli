from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button
from textual.screen import Screen
from tui.widgets.chat_input import ChatInput
from tui.widgets.chat_log import ChatLog
from tui.widgets.choose_panel import ChoosePanel
from tui.widgets.chats_sidebar import ChatSidebar


class ChatScreen(Screen):

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield ChatSidebar(id="sidebar")
            
            with Vertical(id="chat_panel"):
                yield ChatLog(id="chat_log")
                yield ChatInput(id="chat_input")

            yield ChoosePanel(id="info_panel")

    def on_mount(self) -> None:
        """Загружает историю последнего активного чата."""
        if self.app.current_chat_id:
            self.switch_to_chat(self.app.current_chat_id)


    def switch_to_chat(self, chat_id: int) -> None:
        """Переключает активный чат и обновляет лог чата"""
        self.app.current_chat_id = chat_id
        
        chat_log = self.query_one("#chat_log")
        chat_log.query("*").remove()

        history = self.app.db.get_all_chat_messages(chat_id)
        for row in history:
            is_user = (row["role"] == "user")
            chat_log.append_message(row["content"], is_user=is_user)
            
        from tui.widgets.chat_item import ChatItem
        for item in self.query(ChatItem):
            btn = item.query_one("#btn_select")
            if item.chat_id == chat_id:
                btn.add_class("active-chat")
            else:
                btn.remove_class("active-chat")