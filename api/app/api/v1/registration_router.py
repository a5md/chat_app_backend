from fastapi import APIRouter,Depends,Response
from ...dependencies.services import Registration_service
from ...dependencies.services_dependencies import get_registration_service
from ...dependencies.rate_limiter import ip_rate_limit
from ...schemas.user_schema import Register_req,Verify_otp_req,Email_schema

router = APIRouter(
    prefix="/registration" ,tags=["registration"],
    dependencies=[
        Depends(ip_rate_limit)
    ]
)

@router.post("/register")
async def register(
    req : Register_req,
    registration_service:Registration_service =Depends(get_registration_service),
    ):
    return await registration_service.register(
        req=req
        )

@router.post("/register/verify")
async def verify_register(
    req:Verify_otp_req,
    response:Response,
    registration_service:Registration_service =Depends(get_registration_service)
):
    return await registration_service.verify_register(req=req , response=response)

@router.post("/forgot-password")
async def forgot_password(
    req:Email_schema,
    response:Response,
    registration_service:Registration_service =Depends(get_registration_service)
):
    return await registration_service.forgot_password(
        req=req
    )

@router.post("/verify-forgot-password")
async def verify_forgot_password(
    req:Verify_otp_req,
    response:Response,
    registration_service:Registration_service =Depends(get_registration_service)
):
    return await registration_service.verify_forgot_password(
        response=response,
        req=req,
    )