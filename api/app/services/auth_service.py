from fastapi import Response,Request
from beanie import PydanticObjectId
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError,jwt
from ..core.config import settings
from redis.asyncio import Redis
from ..core.exceptions import unauthorized_exception,not_found_exception
from ..models.user import User
from ..services.token_service import Token_service
from ..services.jwt_service import Jwt_service
from ..utils.hash_service import Hash_service
from ..schemas.internal.token_schema import Token_payload


class Auth_service:
    def __init__(
        self,
        redis_client : Redis,
        token_service : Token_service,
        hash_service : Hash_service,
        jwt_service : Jwt_service,
    ):
        self.token_service = token_service
        self.hash_service = hash_service
        self.jwt_service = jwt_service
        self.redis_client = redis_client

    async def login(
            self,
            response:Response,
            user : OAuth2PasswordRequestForm,
            web_client : bool
    ):
        db_user = await User.find_one(User.email == user.username.lower().strip())
        if not db_user:
            raise unauthorized_exception()
        
        if not self.hash_service.verify(user.password , db_user.password_hash):
            raise unauthorized_exception()
        
        payload = Token_payload(
            id= str(db_user.id),
            role= db_user.role,
            is_complete= db_user.user_name is not None
        )
        return await self.token_service.create_session(
            response=response, web_client= web_client , payload= payload
        )
    
    async def refresh(
        self,
        request: Request,
        response: Response,
        refresh_token : str = None,
    ):
        web_client = False
        if not refresh_token:
            refresh_token = request.cookies.get("refresh_token")
            web_client = True
        if not refresh_token:
            raise unauthorized_exception("Refresh token missing") 

        try:
            # 1 decode token
            decoded = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            # 2 get token data
            user_id = decoded.get("id")
            session_id = decoded.get("session_id")
            if decoded.get("type") != "refresh" or not session_id or not user_id:
                raise unauthorized_exception("Invalid token")
            
            # 3 get redis token
            redis_token = await self.redis_client.get(f"jwt:{user_id}:{session_id}")
            if not redis_token:
                raise unauthorized_exception("Invalid or expired session")

            if isinstance(redis_token, bytes):
                redis_token = redis_token.decode() #converting a bytes object into a normal Python string

            # 4 check if it the same token
            if not self.hash_service.verify_token(refresh_token,redis_token):
                raise unauthorized_exception("Token mismatch (possible reuse)")

            # 5 delete the token 
            await self.redis_client.delete(f"jwt:{user_id}:{session_id}")

            # 6 get the data form the DB to create new token
            db_user = await User.get(PydanticObjectId(user_id))
            if not db_user:
                raise not_found_exception("user not found")

            payload = Token_payload(
                id=str(db_user.id),
                role=db_user.role,
                is_complete=db_user.user_name is not None
                )
            return await self.token_service.create_session(
                response=response, web_client= web_client , payload= payload
            )

        except JWTError:
            raise unauthorized_exception()
    
    async def logout(
        self,
        response: Response,
        request: Request,
        refresh_token: str = None
    ):
        web_client = False

        if not refresh_token:
            refresh_token = request.cookies.get("refresh_token")
            web_client = True

        if not refresh_token:
            raise unauthorized_exception("Refresh token missing")

        try:
            decoded = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            if decoded.get("type") != "refresh":
                raise unauthorized_exception("Invalid token")

            user_id = decoded.get("id")
            session_id = decoded.get("session_id")

            if not user_id or not session_id:
                raise unauthorized_exception("Invalid token")

            await self.token_service.delete_session(
                response=response,
                user_id=user_id,
                session_id=session_id,
                web_client=web_client
            )

            return {
                "message": "Logged out successfully"
            }

        except JWTError:
            raise unauthorized_exception("Invalid refresh token")
        


        