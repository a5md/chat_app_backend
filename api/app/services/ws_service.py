from fastapi import WebSocket, WebSocketDisconnect

from ..websocket.manager import Ws_manager
from ..websocket.pub_sub import RedisBackend
from ..schemas.internal.token_schema import Token_payload


class Ws_service:
    def __init__(
        self,
        ws_manager: Ws_manager,
        redisBackend: RedisBackend
    ):
        self.ws_manager = ws_manager
        self.redisBackend = redisBackend


    async def message_ws(
        self,
        websocket: WebSocket,
        current_user: Token_payload
    ):
        await self.ws_manager.connect(
            user_id=current_user.id,
            websocket=websocket
        )

        await self.redisBackend.subscribe(
            channel=current_user.id
        )

        try:
            while True:
                await websocket.receive()

        except WebSocketDisconnect:
            pass

        finally:
            await self.redisBackend.unsubscribe(
                channel=current_user.id
            )

            self.ws_manager.disconnect(
                user_id=current_user.id,
                websocket=websocket
            )
