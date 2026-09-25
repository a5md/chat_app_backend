from ..websocket.manager import Ws_manager
from ..websocket.pub_sub import RedisBackend
import json


class Redis_dispatcher:
    def __init__(
        self,
        redis_backend: RedisBackend,
        ws_manager: Ws_manager,
    ):
        self.redis_backend = redis_backend
        self.ws_manager = ws_manager


    async def run(self):
        while True:
            event = await self.redis_backend.next_published()
            
            try:
                await self.ws_manager.send_to_user(
                    user_id=event.channel,
                    message=json.loads(event.message),
                )
                print(event)
            except Exception:
                print("Failed to dispatch event on channel %s", event.channel)