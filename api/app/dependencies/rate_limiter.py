from ..database.redis import redis_client
from fastapi import HTTPException,status,Request,Depends
from .current_user import get_token_payload

async def check_rate_limit(
    key: str,
    limit: int,
    window: int
):
    count = await redis_client.incr(key)

    if count == 1:
        await redis_client.expire(key, window)

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )


# user id ================================================
async def user_rate_limit(
    token_payload  = Depends(get_token_payload)
):
    key = f"rate:user:{token_payload.id}"

    await check_rate_limit(
        key=key,
        limit=100,
        window=60
    )


# IP ==================================================
async def ip_rate_limit(
    request: Request
):

    ip = request.client.host

    key = f"rate:ip:{ip}"

    await check_rate_limit(
        key=key,
        limit=100,
        window=60
    )