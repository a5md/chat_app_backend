from fastapi import APIRouter,Depends,Response
from ...dependencies.services import Oauth2_service
from ...dependencies.services_dependencies import get_oauth2_service
from ...dependencies.rate_limiter import ip_rate_limit
from ...schemas.oauth2_schema import GoogleSignInRequest


router = APIRouter(
    prefix="/oauth2" ,tags=["oauth2"],
    dependencies=[
        Depends(ip_rate_limit)
    ]
)

@router.post("/google/signin") 
async def login(
    req:GoogleSignInRequest,
    response:Response,
    oauth2_service:Oauth2_service = Depends(get_oauth2_service) ,
    ):
    return await oauth2_service.verify_google_token(
        req=req, 
        response=response
    )