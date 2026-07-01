from textual.app import ComposeResult
from textual.containers import VerticalScroll, Vertical
from textual.widgets import Button
from tui.widgets.chat_item import ChatItem

class ChatSidebar(Vertical):
    """Боковая панель, содержащая кнопку создания и список чатов"""
    
    def compose(self) -> ComposeResult:
        yield Button("New chat", id="btn_create_chat")
        with VerticalScroll(id="chat_list"):
            # Здесь будут динамически добавляться элементы чата
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Обрабатывает нажатия на кнопки внутри сайдбара"""
        if event.button.id == "btn_create_chat":

            new_chat_id = self.app.db.create_chat("Новый чат")
            
            new_item = ChatItem(chat_id=new_chat_id, title="Новый чат")
            
            chat_list = self.query_one("#chat_list")
            chat_list.mount(new_item)
            
            new_item.scroll_visible()