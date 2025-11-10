import asyncio
import json
import pyperclip
from websockets.asyncio.client import connect
from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Input, LoadingIndicator
from textual.containers import Horizontal, Container

from screens.menu_screen import MenuScreen


class ClientApp(App):
    BINDINGS = []
    TITLE = "Poker.py Client"

    def __init__(self):
        self.websocket = None
        super().__init__()

    async def on_mount(self) -> None:
        try:
            self.websocket = await connect("ws://localhost:8001")
            self.notify("Connected to server", severity="information")
            asyncio.create_task(self.listen_for_events())

            await self.push_screen(MenuScreen())
        except Exception as e:
            self.notify(f"Failed to connect to server: [yellow i]{e}[/]\nApplication [bold]WILL NOT WORK AS EXPECTED",
                        severity="error")
            return

        asyncio.create_task(self.listen_for_events())

    async def listen_for_events(self):
        async for message in self.websocket:
            try:
                data = json.loads(message)
                if data["type"] == "game_created":
                    self.notify(f"Game created: {data['data']['code']}")
            except json.JSONDecodeError:
                self.notify("Received invalid JSON from server.")

    async def _on_exit_app(self) -> None:
        if self.websocket:
            await self.websocket.close()


if __name__ == "__main__":
    # asyncio.run(main())
    app = ClientApp()
    app.run()
