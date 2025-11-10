from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input, Button, LoadingIndicator
from textual.containers import Container, Horizontal

import json


class MenuScreen(Screen):
    CSS = """
    Screen {
        align: center middle;
    }
    #menu_container {
        width: 50;
        height: auto;
        border: solid $primary;
        padding: 2 4;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: $success;
        margin-bottom: 2;
    }
    
    #join_container {
        height: auto;
        margin-bottom: 1;
    }
    
    #name_input {
        width: 100%;
        margin-bottom: 1;
    }
    
    #code_input {
        width: 1fr;
        margin-right: 1;
    }
    
    #join_button {
        width: auto;
        min-width: 10;
    }
    
    #join_loading {
        width: auto;
        min-width: 10;
        display: none;
    }
    
    #join_loading.visible {
        display: block;
    }
    
    #create_button {
        width: 100%;
    }
    
    #create_loading {
        width: auto;
        min-width: 10;
        display: none;
    }
    
    #create_loading.visible {
        display: block;
    }
    
    #name_input.invalid {
        border: double $error;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="menu_container"):
            yield Static("╔═══════════════════╗\n║  P O K E R . P Y  ║\n╚═══════════════════╝", id="title")
            yield Input(placeholder="Player Name", id="name_input", type="text")
            with Horizontal(id="join_container"):
                yield Input(placeholder="Join Code", id="code_input", type="text")
                yield Button("Join", id="join_button", variant="primary")
                yield LoadingIndicator(id="join_loading")
            yield Button("Create Room", id="create_button", variant="success")
            yield LoadingIndicator(id="create_loading")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        join_input = self.query_one("#code_input", Input)
        name_input = self.query_one("#name_input", Input)
        join_button = self.query_one("#join_button", Button)
        join_loading = self.query_one("#join_loading", LoadingIndicator)
        create_loading = self.query_one("#create_loading", LoadingIndicator)
        create_button = self.query_one("#create_button", Button)

        join_input.disabled = True
        join_button.disabled = True
        create_button.disabled = True

        if name_input.value.strip() == "":
            self.notify("Please enter a player name.", severity="warning")
            join_input.disabled = False
            join_button.disabled = False
            create_button.disabled = False
            name_input.add_class("invalid")
            return

        if button_id == "join_button":
            join_button.display = False
            join_loading.add_class("visible")

            await self.app.websocket.send(json.dumps({
                "type": "join",
                "data": {"code": join_input.value, "name": name_input.value}
            }))

            self.notify(f"Joining Room: {join_input.value}")

        if button_id == "create_button":
            create_button.display = False
            create_loading.add_class("visible")

            await self.app.websocket.send(json.dumps({
                "type": "create_game",
                "data": {"name": name_input.value}
            }))
