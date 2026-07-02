from textual.app import App
from textual.screen import Screen
from tui.widgets.chat_item import ChatItem 

class ChatManager:
    def __init__(self) -> None:
        pass

    def create_new_chat(self, app: "App", screen: "Screen", title: str = "New Chat") -> int:
        """Создает новый чат"""
        
        new_chat_id = app.db.create_chat(title)
        
        new_item = ChatItem(chat_id=new_chat_id, title=title)
        chat_list = screen.query_one("#chat_list")
        chat_list.mount(new_item)
        
        screen.switch_to_chat(new_chat_id)
        return new_chat_id

    def delete_chat(self, app: "App", screen: "Screen", chat_item: "ChatItem") -> None:
        """Удаляет текущей чат чат"""
        
        app.db.delete_chat(chat_item.chat_id)
        if chat_item.chat_id == app.current_chat_id:
            all_items = list(screen.query(ChatItem))
            remaining_items = [item for item in all_items if item != chat_item]
            if remaining_items:
                screen.switch_to_chat(remaining_items[0].chat_id)
            else:
                self.create_new_chat(app, screen, "New Chat")
        
        chat_item.remove()
    
    def rename_chat(self, app: "App", chat_item: "ChatItem", new_title: str) -> None:
        """Переименовывает чат"""
        
        if new_title.strip():
            chat_item.chat_title = new_title
            app.db.update_chat_title(chat_item.chat_id, new_title)
            
            if chat_item.chat_id == app.current_chat_id:
                app.current_chat_title = new_title
            
            btn_select = chat_item.query_one("#btn_select")
            btn_select.label = new_title