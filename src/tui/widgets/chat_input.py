from textual.widgets import Input

class ChatInput(Input):
    def __init__(self, id = None):
        super().__init__(placeholder="Input your request...", id = id)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        if not prompt:
            return
        
        self.value = ""
        
        chat_log = self.screen.query_one("#chat_log")
        
        chat_log.append_message("User", prompt)
        
        bot_response = ""
        try:
            async for chunk in self.app.engine.get_chat_stream(
                message=prompt, 
                model=self.app.model, 
                provider=self.app.provider
            ):
                bot_response += chunk
            
            chat_log.append_message(self.app.model, bot_response)
        
        except Exception as e:
            chat_log.append_message("Engine error:", str(e), "red")