from contextlib import asynccontextmanager
import asyncio

from ..database.mongodb import init_db, close_db
from ..database.redis import init_redis, close_redis
from ..dependencies.services import (
    redisBackend,
    redis_dispatcher
)


@asynccontextmanager
async def lifespan(app):

    # startup
    await init_db()
    await init_redis()

    listener_task = asyncio.create_task(
        redisBackend._pubsub_listener()
    )

    dispatcher_task = asyncio.create_task(
        redis_dispatcher.run()
    )

    try:
        yield

    finally:
        # shutdown
        listener_task.cancel()
        dispatcher_task.cancel()

        await asyncio.gather(
            listener_task,
            dispatcher_task,
            return_exceptions=True
        )

        await close_db()
        await close_redis()