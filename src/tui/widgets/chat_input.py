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
        
        # Сообщение пользователя и бота
        chat_log.append_message(prompt, is_user=True)
        bot_msg = chat_log.append_message("", is_user=False)
        
        chat_log.scroll_end(animate=False)

        bot_response = ""
        try:
            async for chunk in self.app.engine.get_chat_stream(
                message=prompt, 
                model=self.app.model, 
                provider=self.app.provider
            ):
                
                bot_response += chunk
                bot_msg.update_content(bot_response)
                chat_log.scroll_end(animate=False)
        
        except Exception as e:
            bot_msg.update_content(f"[red]Ошибка движка: {e}[/red]")