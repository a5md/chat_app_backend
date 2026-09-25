from fastapi import APIRouter,Depends,Query
from beanie import PydanticObjectId
from ...dependencies.services import Conversation_service
from ...dependencies.services_dependencies import get_conversation_service
from ...dependencies.current_user import get_current_user
from ...dependencies.rate_limiter import user_rate_limit
from ...schemas.conversation_schema import Conversation_res,Conversations_res

router = APIRouter(
    prefix="/conversaton" ,tags=["conversaton"] ,
    dependencies=[
        Depends(user_rate_limit)
    ]
)

@router.post("/" , response_model=Conversation_res)
async def start_conversation(
    target_user_id:PydanticObjectId,
    current_user = Depends(get_current_user),
    conversation_service:Conversation_service = Depends(get_conversation_service)
):
    return await conversation_service.start_conversation(
        target_user_id=target_user_id,
        current_user=current_user
    )

@router.get("/" ,response_model=Conversations_res)
async def get_conversations(
    skip:int | None = 0,
    current_user = Depends(get_current_user),
    conversation_service:Conversation_service = Depends(get_conversation_service)
):
    return await conversation_service.get_conversations(
        skip=skip,
        current_user=current_user
    )

@router.get("/{conversation_id}" ,response_model=Conversation_res)
async def get_conversation(
    conversation_id:PydanticObjectId,
    current_user = Depends(get_current_user),
    conversation_service:Conversation_service = Depends(get_conversation_service)
):
    return await conversation_service.get_conversation(
        conversation_id=conversation_id,
        current_user=current_user
    )