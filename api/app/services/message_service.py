from beanie.operators import Set,And
from beanie import UpdateResponse,PydanticObjectId
from datetime import datetime,timezone
from ..models.message import Message
from ..models.conversation import Conversation
from ..schemas.internal.token_schema import Token_payload
from ..schemas.message_schema import Message_req ,Messages_res,Message_res
from ..core.exceptions import not_found_exception
from ..websocket.pub_sub import RedisBackend

class Message_service:
    def __init__(
            self,
            redisBackend:RedisBackend
            ):
        self.redisBackend = redisBackend

    async def send_message(
        self,
        current_user:Token_payload,
        message:Message_req,
    ):
        conversation_db = await Conversation.find_one(
            And(
            Conversation.id == message.conversation_id,
            Conversation.members == current_user.id,
            )
        ).update(
            Set({
                Conversation.last_message: message.content,
                Conversation.last_message_at: datetime.utcnow(),
            }),
            response_type=UpdateResponse.NEW_DOCUMENT,
        )
        if not conversation_db :
            raise not_found_exception()

        new_message = Message(
            content=message.content,
            conversation_id=str(message.conversation_id),
            sender_id=str(current_user.id)
        )
        await new_message.insert()

        for member_id in conversation_db.members:
            await self.redisBackend.publish(
                channel=member_id,
                message=new_message.model_dump_json(),
            )

        return new_message

    async def get_messages(
        self,
        conversation_id:PydanticObjectId,
        oldest:datetime | None,
        current_user:Token_payload
    ):
        #find the conversation
        conversation_db = await Conversation.find_one(
            And(Conversation.id == conversation_id , Conversation.members == current_user.id)
        )
        if not conversation_db:
            raise not_found_exception()

        if oldest is None:
            oldest = datetime.now(timezone.utc)

        limit = 20
        messages = await Message.find(
            And(Message.conversation_id == str(conversation_id),
                Message.created_at < oldest)
        ).sort(-Message.created_at).limit(limit).to_list()

        return Messages_res(
            messages=[Message_res(**m.model_dump()) for m in messages],
            next_oldest = messages[-1].created_at if len(messages) == limit else None
        )