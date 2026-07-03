from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, OptionList, Select
from textual.widgets.option_list import Option


class ChoosePanel(Vertical):

    def compose(self) -> ComposeResult:
        models = [model for model in self.app.engine.get_all_models() if model]

        if models and self.app.model not in models:
            fallback_model = self.app.DEFAULT_MODEL if self.app.DEFAULT_MODEL in models else models[0]
            self.app.model = fallback_model

        yield Label("Model", id="model_label")
        yield Select(
            [(m, m) for m in models],
            value=self.app.model if models else Select.BLANK,
            id="model",
            disabled=not models,
        )

        Provider_List = OptionList(id="providers")
        Provider_List.border_title = "Providers"
        yield Provider_List

    def on_mount(self):
        self.load_providers(self.app.model)

    def load_providers(self, model: str) -> list[str]:

        option_list = self.query_one("#providers", OptionList)
        option_list.clear_options()
        option_list.add_option(Option("Auto"))

        providers = sorted(
            p.name
            for p in self.app.engine.get_available_providers()
            if model in p.supported_models
        )

        for provider in providers:
            option_list.add_option(Option(provider))

        return providers


    def on_select_changed(self, event: Select.Changed):

        if event.select.id != "model":
            return

        if event.value == Select.BLANK:
            return

        model = str(event.value)
        if model == self.app.model:
            return

        self.app.model = model
        providers = self.load_providers(self.app.model)
        if self.app.provider not in providers:
            self.app.provider = None

        self.app.config.update_config(model=self.app.model, provider=self.app.provider)


    def on_option_list_option_selected(self, event: OptionList.OptionSelected):

        text = str(event.option.prompt)
        self.app.provider = None if text == "Auto" else text
        self.app.config.update_config(model=self.app.model, provider=self.app.provider)
