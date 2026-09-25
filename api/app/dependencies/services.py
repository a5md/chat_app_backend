from ..database.redis import redis_client
from ..utils.hash_service import Hash_service
from ..services.email_service import Email_service
from ..services.jwt_service import Jwt_service
from ..services.otp_service import Otp_service
from ..services.token_service import Token_service
from ..services.registration_service import Registration_service
from ..services.auth_service import Auth_service
from ..services.user_service import User_service
from ..services.conversation_service import Conversation_service
from ..services.oauth2_service import Oauth2_service
from ..services.message_service import Message_service
from ..services.ws_service import Ws_service

from ..websocket.dispatcher import Redis_dispatcher
from ..websocket.manager import Ws_manager
from ..websocket.pub_sub import RedisBackend


#================ WS ==================================================================================

ws_manager = Ws_manager()

redisBackend = RedisBackend(
    redis_client=redis_client,
)

redis_dispatcher = Redis_dispatcher(
    redis_backend=redisBackend,
    ws_manager=ws_manager
)   

ws_service = Ws_service(
    ws_manager=ws_manager,
    redisBackend=redisBackend
)

#=====================================================================================================

hash_service = Hash_service()

otp_service = Otp_service(
    hash_service=hash_service
)

jwt_service = Jwt_service()
token_service = Token_service(
    jwt_service=jwt_service,
    redis_client=redis_client,
    hash_service=hash_service
)

email_service = Email_service(
    redis_client=redis_client
)

auth_service = Auth_service(
    redis_client=redis_client,
    hash_service= hash_service,
    token_service= token_service,
    jwt_service=jwt_service,
)

oauth2_service = Oauth2_service(
    token_service=token_service,
    email_service=email_service
)

registration_service = Registration_service(
    redis_client=redis_client,
    otp_service=otp_service,
    hash_service=hash_service,
    email_service=email_service,
    token_service=token_service
)

user_service= User_service(
    redis_client=redis_client,
    hash_service=hash_service
)

conversation_service = Conversation_service(
    redis_client=redis_client
)

message_service = Message_service(
    redisBackend=redisBackend
)




