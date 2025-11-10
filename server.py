from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosedOK
import asyncio

import json

class Event:
    def __init__(self, type: str, data: dict):
        try:
            self.type: str = type
            self.data: dict = data
        except Exception as e:
            raise ValueError(f"Invalid event data: {e}")

class Poker:
    def __init__(self):
        pass


async def handler(websocket: ServerConnection):
    while True:
        try:
            message: dict = json.loads(await websocket.recv())

            event = Event(type=message.get("type"), data=message.get("data"))

            if event.type == "message":
                print(f"Received message: {event.data['message']}")
                response = {"response": f"Echo: {event.data['message']}"}
                await websocket.send(json.dumps(response))

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


if __name__ == "__main__":
    asyncio.run(main())
