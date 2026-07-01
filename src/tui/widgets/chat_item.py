from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button

class ChatItem(Widget):
    """Компонент одной строки чата в списке"""
    
    def __init__(self, chat_id: int, title: str, is_active: bool = False) -> None:
        super().__init__(id=f"chat_item_{chat_id}")
        self.chat_id = chat_id
        self.chat_title = title
        self.is_active = is_active

    def compose(self) -> ComposeResult:
        with Horizontal(classes="chat-item-row"):
            yield Button(
                self.chat_title, 
                id="btn_select", 
                classes="active-chat" if self.is_active else ""
            )
            yield Button("Rename", id="btn_rename", classes="btn-action")
            yield Button("Del", id="btn_delete", classes="btn-action variant-error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        
        if event.button.id == "btn_select":
            self.screen.switch_to_chat(self.chat_id)
            
        elif event.button.id == "btn_delete":
            self.app.db.delete_chat(self.chat_id)
            
            if self.chat_id == self.app.current_chat_id:
                all_items = list(self.screen.query(ChatItem))
                remaining_items = [item for item in all_items if item != self]
                
                if remaining_items:
                    self.screen.switch_to_chat(remaining_items[0].chat_id)
                else:
                    new_chat_id = self.app.db.create_chat("Main chat")
                    new_item = ChatItem(chat_id=new_chat_id, title="Main chat")
                    
                    chat_list = self.screen.query_one("#chat_list")
                    chat_list.mount(new_item)
                    
                    self.screen.switch_to_chat(new_chat_id)
            
            self.remove()