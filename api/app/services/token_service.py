from .jwt_service import Jwt_service
from ..core.config import settings
from ..utils.hash_service import Hash_service
from redis.asyncio import Redis
from ..schemas.internal.token_schema import Token_payload
from fastapi import Response
import uuid

class Token_service:
    def __init__(
            self, 
            jwt_service:Jwt_service,
            redis_client:Redis,
            hash_service:Hash_service
            ):
        self.jwt_service = jwt_service
        self.redis_client = redis_client
        self.hash_service = hash_service

    async def create_session(self, payload:Token_payload ,response:Response ,web_client : bool = True):
        access_token = self.jwt_service.create_access_token(
            payload.model_dump()
        )

        session_id = str(uuid.uuid4()) #create session id for many devises support
        refresh_payload = {
            **payload.model_dump(),
            "session_id": session_id
        }

        refresh_token = self.jwt_service.create_refresh_token(
            refresh_payload
        )

        hashed_refresh_token = self.hash_service.hash_token(refresh_token)

        # store refresh token in Redis hashed
        await self.redis_client.set(
            f"jwt:{payload.id}:{session_id}",
            hashed_refresh_token,
            ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        )

        if web_client:
            # set refresh token cookie
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure= not settings.DEBUG,  # True in production (HTTPS)
                samesite="lax",
                path="/",
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
            )

            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        
        #not web client
        return {
            "refresh_token":refresh_token,
            "access_token": access_token,
            "token_type": "bearer"
        }

    async def delete_session(
            self,
            response:Response,
            user_id :str,
            session_id:str,
            web_client : bool = True
    ):
        # delete refresh token session from Redis
        await self.redis_client.delete(
            f"jwt:{user_id}:{session_id}"
        )

        # delete cookie only for web client
        if web_client:
            response.delete_cookie(
                key="refresh_token",
                httponly=True,
                secure= not settings.DEBUG,  # True in production (HTTPS)
                path="/",
            )
        
        