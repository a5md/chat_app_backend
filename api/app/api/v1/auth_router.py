from fastapi import APIRouter,Depends,Response,Request
from fastapi.security import OAuth2PasswordRequestForm
from ...dependencies.services import Auth_service
from ...dependencies.rate_limiter import ip_rate_limit
from ...dependencies.services_dependencies import get_auth_service
from ...schemas.internal.token_schema import Token_req


router = APIRouter(
    prefix="/auth" ,tags=["auth"],
    dependencies=[
            Depends(ip_rate_limit)
        ]
)

@router.post("/login") 
async def login(
    response:Response,
    web_client : bool = True,
    auth_service:Auth_service = Depends(get_auth_service) ,
    user: OAuth2PasswordRequestForm = Depends()
    ):
    return await auth_service.login(
        response=response,
        user=user,
        web_client=web_client 
    )

@router.post("/refresh")
async def refresh(
    response:Response,
    request:Request,
    req : Token_req,
    auth_service:Auth_service = Depends(get_auth_service) ,
):
    return await auth_service.refresh(
        response=response,
        request=request,
        refresh_token=req.token,
    )

@router.post("/logout")
async def logout(
    response:Response,
    request:Request,
    refresh_token:str | None = None,
    auth_service:Auth_service = Depends(get_auth_service) ,
):
    return await auth_service.logout(
        response=response,
        request=request,
        refresh_token=refresh_token,
    )