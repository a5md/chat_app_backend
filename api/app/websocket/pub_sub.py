import asyncio
import typing
from redis.asyncio import Redis
from pydantic import BaseModel

class Event(BaseModel):
    channel: str
    message: typing.Any

class RedisBackend():

    def __init__(
            self,
            redis_client : Redis
            ):
        self.redis_client = redis_client

        self._pubsub = self.redis_client.pubsub()
        self._ready = asyncio.Event()
        self._queue: asyncio.Queue[Event] = asyncio.Queue()

    async def subscribe(self, channel: str) -> None: #Used when a user connects to your WebSocket.
        await self._pubsub.subscribe(channel)
        self._ready.set()

    async def unsubscribe(self, channel: str) -> None:
        await self._pubsub.unsubscribe(channel)

    async def publish(self, channel: str, message: typing.Any) -> None:#when you want to send a message to another user
        await self.redis_client.publish(
            channel,
            message
        )

    async def next_published(self):
        return await self._queue.get()

    async def _pubsub_listener(self) -> None: #Start it once when FastAPI starts.
        # redis-py does not listen to the pubsub connection if there are no channels subscribed
        # so we need to wait until the first channel is subscribed to start listening
        while True:
            await self._ready.wait()
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    event = Event(
                        channel=message["channel"],
                        message=message["data"],
                    )
                    await self._queue.put(event)

            # when no channel subscribed, clear the event.
            # And then in next loop, event will blocked again until
            # the new channel subscribed.Now asyncio.Task will not exit again.
            self._ready.clear()
         