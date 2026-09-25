from redis.asyncio import Redis
from ..models.conversation import Conversation
from ..models.user import User
from beanie import PydanticObjectId
from ..schemas.conversation_schema import Conversation_res
from ..schemas.internal.token_schema import Token_payload
from ..core.exceptions import (
    conflict_exception,
    not_found_exception,
    bad_request_exception)
    
class Conversation_service:
    def __init__(
              self,
              redis_client:Redis,
            ):
        self.redis_client = redis_client,

    async def start_conversation(
            self,
            current_user:Token_payload,
            target_user_id:PydanticObjectId
    ):
        if current_user.id == str(target_user_id):
            raise bad_request_exception("You cannot start a conversation with yourself")
        
        members = sorted([current_user.id, str(target_user_id)])

        target_user = await User.get(target_user_id)
        if not target_user:
            raise not_found_exception("User not found")
        
        conversation_db = await Conversation.find_one(
            Conversation.members == members
        )
        if conversation_db:
            raise conflict_exception()

        current_user_db = await User.get(
        PydanticObjectId(current_user.id)
    )

        conversation = Conversation(
            members=members,
            users=[
                {
                    "id": str(current_user_db.id),
                    "user_name": current_user_db.user_name,
                    "avatar": current_user_db.avatar
                },
                {
                    "id": str(target_user.id),
                    "user_name": target_user.user_name,
                    "avatar": target_user.avatar
                }
            ]
        )
        await conversation.insert()

        return Conversation_res(
            id=conversation.id,
            user_name=target_user.user_name,
            avatar=target_user.avatar,
            members=conversation.members,
            last_message=conversation.last_message,
            last_message_at=conversation.last_message_at,
            created_at=conversation.created_at
        )

    async def get_conversations(
            self,
            current_user:Token_payload,
            skip:int
    ):
        limit = 20

        conversations = await Conversation.find(
            Conversation.members == current_user.id
        ).sort(-Conversation.last_message_at).skip(skip).limit(limit).to_list()

        result = []

        for c in conversations:
            other_user = None

            for user in c.users:
                if user.id != current_user.id:
                    other_user = user
                    break

            if other_user:
                result.append(
                    Conversation_res(
                        id=c.id,
                        user_name=other_user.user_name,
                        avatar=other_user.avatar,
                        members=c.members,
                        last_message=c.last_message,
                        last_message_at=c.last_message_at,
                        created_at=c.created_at
                    )
                )

        return {
            "conversations": result,
            "next_skip": skip + limit if len(conversations) == limit else None
        }

    async def get_conversation(
            self,
            current_user: Token_payload,
            conversation_id: PydanticObjectId
    ):
        conversation = await Conversation.find_one(
            Conversation.id == conversation_id,
            Conversation.members == current_user.id
        )

        if not conversation:
            raise not_found_exception()

        for user in conversation.users:
            if user.id != current_user.id:
                target_user = user
                
        if not target_user:
            raise not_found_exception()

        return Conversation_res(
            id=conversation.id,
            user_name=target_user.user_name,
            avatar=target_user.avatar,
            members=conversation.members,
            last_message=conversation.last_message,
            last_message_at=conversation.last_message_at,
            created_at=conversation.created_at
        )
        


        

