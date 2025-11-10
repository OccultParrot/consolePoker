from dataclasses import dataclass

from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosedOK
import asyncio
from uuid import uuid4 as uuid
import secrets

import json


@dataclass
class Player:
    id: str
    name: str
    connection: ServerConnection
    is_host: bool = False

    def __init__(self, name: str, connection: ServerConnection):
        self.id = str(uuid())
        self.name = name
        self.connection = connection


class Event:
    """
    Represents an event with a type and associated data.
    """

    def __init__(self, event_type: str, event_data: dict = {}):
        """
        Initializes an Event instance.
        :param event_type: Events type as a string.
        :param event_data: The data associated with the event as a dictionary.
        """
        try:
            self.type: str = event_type
            self.data: dict = event_data
        except Exception as e:
            raise ValueError(f"Invalid event data: {e}")

    def to_json(self):
        """
        Converts the Event instance to a JSON string.
        :return: JSON string representation of the event.
        """
        return json.dumps({
            "type": self.type,
            "data": self.data
        })

    @staticmethod
    def player_joined(player: 'Player') -> 'Event':
        """
        Creates an event indicating a player has joined the game.
        :param player: The player who joined.
        :return: Event instance.
        """
        return Event(event_type="player_joined", event_data={
            "id": player.id,
            "name": player.name,
        })

    @staticmethod
    def game_joined(game: 'Game', you: 'Player') -> 'Event':
        return Event(event_type="game_joined", event_data={
            "your_id": you.id,
            "code": game.code,
            "players": [
                {
                    "is_host": player.is_host,
                    "id": player.id,
                    "name": player.name
                } for i, player in enumerate(game.players)
            ]
        })

    @staticmethod
    def player_left(player: 'Player') -> 'Event':
        """
        Creates an event indicating a player has left the game.
        :param player: The player who left.
        :return: Event instance.
        """
        return Event(event_type="player_left", event_data={
            "player_id": player.id,
            "player_name": player.name,
        })

    @staticmethod
    def game_left() -> 'Event':
        return Event(event_type="game_left")


class Game:
    def __init__(self):
        self.players: list[Player] = []
        self.code = secrets.token_hex(4)

    def add_player(self, connection: ServerConnection, code: str, name: str) -> bool:
        if self.code != code:
            return False

        player = Player(name=name, connection=connection)

        if len(self.players) == 0:
            player.is_host = True

        # Notify existing players
        for p in self.players:
            asyncio.create_task(p.connection.send(
                Event.player_joined(player).to_json()
            ))

        self.players.append(player)

        # Send new player their ID and full game state
        asyncio.create_task(connection.send(
            Event.game_joined(self, player).to_json()
        ))
        return True

    def remove_player(self, connection: ServerConnection) -> None:
        for i, player in enumerate(self.players):
            if player.connection == connection:
                self.players.pop(i)

                # Notify remaining players
                for p in self.players:
                    asyncio.create_task(p.connection.send(
                        Event.player_left(player).to_json()
                    ))
                break


async def handler(websocket: ServerConnection):
    # Getting the list of active games
    global games

    while True:
        try:
            # Parsing the event
            message: dict = json.loads(await websocket.recv())
            event = Event(event_type=message.get("type"), event_data=message.get("data"))

            print(event.type, event.data)

            if event.type == "create_game":
                new_game = Game()
                new_game.add_player(websocket, new_game.code, event.data.get("name"))
                games.append(new_game)

            if event.type == "join_game":
                successfully_joined = False
                for g in games:
                    successfully_joined = g.add_player(websocket, event.data.get("code"), event.data.get("name"))
                    if successfully_joined:
                        break

                if not successfully_joined:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "data": {"message": "Invalid game code."}
                    }))

        # Handling connection closure
        except ConnectionClosedOK:
            for g in games:
                g.remove_player(websocket)

                # If the game has no players left, remove it from the active games list
                if len(g.players) == 0:
                    games.remove(g)

            print("Connection closed gracefully.")
            break
        # Handling invalid websocket messages
        except json.JSONDecodeError:
            print("Received invalid JSON, skipping message...")
            continue


async def main():
    async with serve(handler, "", 8001):
        print("WebSocket server started on ws://localhost:8001")
        await asyncio.Future()  # run forever


# The list of active games
games: list[Game] = []

if __name__ == "__main__":
    asyncio.run(main())
