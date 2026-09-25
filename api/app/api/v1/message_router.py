from fastapi import APIRouter,Depends,Query
from beanie import PydanticObjectId
from datetime import datetime
from ...dependencies.services import Message_service
from ...dependencies.services_dependencies import get_message_service
from ...dependencies.current_user import get_current_user
from ...dependencies.rate_limiter import user_rate_limit
from ...schemas.message_schema import Message_req,Message_res,Messages_res

router = APIRouter(
    prefix="/message" ,tags=["message"],
    dependencies=[
        Depends(user_rate_limit)
    ]
)

@router.post("/" , response_model=Message_res)
async def send_message(
    req : Message_req,
    current_user = Depends(get_current_user),
    message_service:Message_service = Depends(get_message_service)
):
    return await message_service.send_message(
        message=req,
        current_user=current_user
    )

@router.get("/{conversation_id}" , response_model=Messages_res)
async def get_messages(
    conversation_id:PydanticObjectId,
    oldest : datetime | None = None,
    current_user = Depends(get_current_user),
    message_service:Message_service = Depends(get_message_service)
):
    return await message_service.get_messages(
        conversation_id=conversation_id,
        oldest=oldest,
        current_user=current_user
    )