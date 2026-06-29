from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Placeholder
from widgets.chat_log import ChatLog
from widgets.chat_input import ChatInput
from core.engine import G4FEngine
from core.config import ConfigManager

class ChatScreen(Screen):
    def __init__(self):
        super().__init__()
        self.engine = G4FEngine()
        self.config = ConfigManager()
        settings = self.config.load_settings()
        self.model = settings["last_model"] if settings else "gpt-4o"
        self.provider = settings["last_provider"]

    def compose(self):
        """Экран чата сайдбар с настройками и чат с логом"""
        with Horizontal():
            yield Vertical(
                Placeholder(),
                id="sidebar_panel") 
            
            with Vertical(id="chat_panel"):
                yield ChatLog(id="chat_log")
                yield ChatInput(id="chat_input")
    
    async def on_input_submitted(self, event: ChatInput.Submitted):
        """"Обработка события отправки сообщения из виджета ChatInput"""
        promt = event.value.strip()
        
        if not promt:
            return
        
        event.input.value = ""

        async for chunk in self.engine.stream_chat(message=promt, model=self.model, provider=self.provider):
            print(chunk) #надо добавить вывод нормальный после того как доделаем chat_log, а это удалить
