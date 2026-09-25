from fastapi import APIRouter
from .registration_router import router as registration_router
from .auth_router import router as auth_router
from .user_router import router as user_router
from .conversation_router import router as conversation_router
from .oauth2_router import router as oauth2_router
from .message_router import router as message_router
from .ws_router import router as ws_router


router = APIRouter(
    prefix="/v1"
)

router.include_router(registration_router)
router.include_router(auth_router)
router.include_router( oauth2_router)
router.include_router(user_router)
router.include_router( conversation_router)
router.include_router( message_router)
router.include_router( ws_router)
