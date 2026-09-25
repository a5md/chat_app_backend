from fastapi import APIRouter,Depends,Query
from ...dependencies.services import User_service
from ...dependencies.current_user import get_current_user
from ...dependencies.services_dependencies import get_user_service
from ...dependencies.rate_limiter import ip_rate_limit,user_rate_limit
from ...schemas.user_schema import Reset_password_req,Me_res,User_id_req,User_res,Bio_req



router = APIRouter(
    prefix="/user" ,tags=["user"] 
)

@router.get("/check/username",dependencies=[Depends(ip_rate_limit)])
async def check_username(
    user_name:str,
    user_service:User_service = Depends(get_user_service) ,
):
    return await user_service.check_username(
        user_name=user_name
    )

@router.put("/reset-password",dependencies=[Depends(user_rate_limit)])
async def reset_password(
    req:Reset_password_req,
    current_user = Depends(get_current_user),
    user_service:User_service = Depends(get_user_service) ,
):
    return await user_service.reset_password(
        req=req,
        current_user=current_user
    )

@router.put("/update-bio",dependencies=[Depends(user_rate_limit)])
async def update_bio(
    req:Bio_req,
    current_user = Depends(get_current_user),
    user_service:User_service = Depends(get_user_service) ,
):
    return await user_service.update_bio(
        req=req,
        current_user=current_user
    )

@router.get("/me", response_model=Me_res , dependencies=[Depends(user_rate_limit)],)
async def get_me(
    current_user = Depends(get_current_user),
    user_service:User_service = Depends(get_user_service) ,
):
    return await user_service.get_me(
        current_user=current_user
    )

@router.delete("/",dependencies=[Depends(user_rate_limit)])
async def delete_user(
    req:User_id_req,
    current_user = Depends(get_current_user),
    user_service:User_service = Depends(get_user_service) ,
):
    return await user_service.delete_user(
        req=req,
        current_user=current_user
    )

@router.get("/search", response_model=list[User_res],dependencies=[Depends(user_rate_limit)],)
async def search_users(
    query: str = Query(..., min_length=1, max_length=30),
    current_user = Depends(get_current_user),
    user_service:User_service = Depends(get_user_service) ,
):
    return await user_service.search_users(req=query ,current_user=current_user)