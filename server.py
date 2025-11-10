from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosedOK
import asyncio
import secrets

import json


class Event:
    def __init__(self, type: str, data: dict):
        try:
            self.type: str = type
            self.data: dict = data
        except Exception as e:
            raise ValueError(f"Invalid event data: {e}")


class Game:
    def __init__(self):
        self.players: list[ServerConnection] = []
        self.code = secrets.token_hex(4)


async def handler(websocket: ServerConnection):
    while True:
        try:
            message: dict = json.loads(await websocket.recv())

            event = Event(type=message.get("type"), data=message.get("data"))

            print(f"Received event: {event.type} with data: {event.data}")

            if event.type == "create":
                game = Game()
                games.append(game)
                response = {
                    "type": "game_created",
                    "data": {"code": game.code}
                }
                await websocket.send(json.dumps(response))
                print(f"Created new game with code: {game.code}")

            elif event.type == "join":
                code = event.data.get("code")
                game = next((g for g in games if g.code == code), None)
                if game:
                    game.players.append(websocket)
                    response = {
                        "type": "joined_game",
                        "data": {"code": game.code, "player_count": len(game.players)}
                    }
                    await websocket.send(json.dumps(response))
                    print(f"Player joined game with code: {game.code}")
                else:
                    response = {
                        "type": "error",
                        "data": {"message": "Game not found"}
                    }
                    await websocket.send(json.dumps(response))
                    print(f"Join failed: Game with code {code} not found")

        except ConnectionClosedOK:
            print("Connection closed normally.")
            break
        except json.JSONDecodeError:
            print("Received invalid JSON, skipping message...")
            continue


async def main():
    async with serve(handler, "", 8001):
        print("WebSocket server started on ws://localhost:8001")
        await asyncio.Future()  # run forever


games: list[Game] = []

if __name__ == "__main__":
    asyncio.run(main())
