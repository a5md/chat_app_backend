from fastapi import WebSocket
from typing import Dict, Set


class Ws_manager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(
        self,
        user_id: str,
        websocket: WebSocket
    ):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)


    def disconnect(
        self,
        user_id: str,
        websocket: WebSocket
    ):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if len(self.active_connections[user_id]) == 0:
                del self.active_connections[user_id]


    async def send_to_user(
        self,
        user_id: str,
        message: dict
    ):
        sockets = self.active_connections.get(user_id)

        if not sockets:
            return

        for socket in sockets:
            await socket.send_json(message)


