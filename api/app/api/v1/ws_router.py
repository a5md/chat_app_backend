from fastapi import APIRouter, Depends, WebSocket
from ...dependencies.services_dependencies import get_ws_service
from ...dependencies.current_user import get_current_user_ws
from ...services.ws_service import Ws_service


router = APIRouter(
    prefix="/ws",
    tags=["ws"]
)


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user = Depends(get_current_user_ws),
    ws_service: Ws_service = Depends(get_ws_service)
):
    await ws_service.message_ws(
        websocket=websocket,
        current_user=current_user
    )