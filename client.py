import asyncio
import json
from websockets.asyncio.client import connect

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        print(f"\nReceived from server: {data}")


async def main():
    async with connect("ws://localhost:8001") as websocket:
        asyncio.create_task(handler(websocket))

        while True:
            user_input = await asyncio.to_thread(input, "Enter message to send (or 'exit' to quit): ")
            if user_input.lower() == "exit":
                break

            event = {
                "type": "message",
                "data": {
                    "message": user_input
                }
            }
            await websocket.send(json.dumps(event))



if __name__ == "__main__":
    asyncio.run(main())
