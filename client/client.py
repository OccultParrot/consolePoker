import asyncio
import json
import argparse
from websockets.asyncio.client import connect

parser = argparse.ArgumentParser(description="Poker Client")
parser.add_argument("--code", type=str, help="Game code to join", required=False)


async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)

        if data.get("type") == "game_created":
            code = data["data"]["code"]
            print(f"\n✓ Game created successfully!")
            print(f"Game code: {code}")
            print(f"Share this code with other players to join.")

        else:
            print(f"\nReceived from server: {data}")


async def main():
    args = parser.parse_args()

    async with connect("ws://localhost:8001") as websocket:
        asyncio.create_task(handler(websocket))

        if args.code:
            join_event = {
                "type": "join",
                "data": {"code": args.code}
            }
            await websocket.send(json.dumps(join_event))
            print(f"Joining game with code: {args.code}")
        else:
            create_event = {
                "type": "create",
                "data": {}
            }
            await websocket.send(json.dumps(create_event))
            print("Creating a new game")

        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
