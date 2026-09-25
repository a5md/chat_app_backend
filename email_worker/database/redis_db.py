from redis.asyncio import Redis
from ..core.config import settings


redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0,
    decode_responses=True,
    socket_timeout=None
)


async def init_redis():
    await redis_client.ping()


async def close_redis():
    await redis_client.close()