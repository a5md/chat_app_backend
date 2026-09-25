from ..core.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,WebSocket, WebSocketException, status
from jose import jwt,JWTError
from ..schemas.internal.token_schema import Token_payload
from ..core.exceptions import unauthorized_exception,forbidden_exception


oauth2_schema = OAuth2PasswordBearer( #get token form the header
    tokenUrl="/api/v1/auth/login" #help on login for the docs only 
    )

def get_token_payload(token:str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])

        user_id :str = payload.get("id")
        role :str = payload.get("role")
        is_complete = payload.get("is_complete", True)

        if user_id is None or role is None:
            raise unauthorized_exception()
        
        return Token_payload(
            id = user_id,
            role = role,
            is_complete = is_complete
            )
    except JWTError:
        raise unauthorized_exception()


def get_current_user(
    token: Token_payload = Depends(get_token_payload)
):
    if not token.is_complete:
        raise forbidden_exception("Complete your profile first")

    return token

def get_uncomplete_user(
    token: Token_payload = Depends(get_token_payload)
):
    return token






async def get_current_user_ws(
    websocket: WebSocket
):
    auth = websocket.headers.get("Authorization")

    if not auth:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION
        )

    if not auth.startswith("Bearer "):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION
        )

    token = auth.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("id")
        role = payload.get("role")
        is_complete = payload.get("is_complete", True)

        if user_id is None or role is None or not is_complete:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION
            )

        return Token_payload(
            id=user_id,
            role=role,
            is_complete=is_complete
        )

    except JWTError:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION
        )