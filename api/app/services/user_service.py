from redis.asyncio import Redis
from ..models.user import User
from beanie import PydanticObjectId
from beanie.operators import RegEx
from ..schemas.user_schema import Reset_password_req ,Me_res, User_id_req,User_res,Bio_req
from ..schemas.internal.token_schema import Token_payload
from ..schemas.internal.user_role_schema import User_role
from ..utils.hash_service import Hash_service
from ..core.exceptions import (
    not_found_exception,
    unauthorized_exception,
    bad_request_exception,
    forbidden_exception)

class User_service:
    def __init__(
            self,
            redis_client:Redis,
            hash_service:Hash_service
            ):
        self.redis_client = redis_client
        self.hash_service = hash_service

    async def check_username(
            self ,
            user_name : str
            ):
        user_db = await User.find_one(User.user_name == user_name)
        user_redis = await self.redis_client.get(f"registration:user_name:{user_name}")
        if user_db or user_redis:
            return {"available":False}
        return {"available":True}
    
    async def reset_password(
            self,
            req:Reset_password_req,
            current_user:Token_payload
    ):
        if req.id and current_user.role == User_role.ADMIN:
            user_id = req.id
        else:
            user_id = current_user.id

        user = await User.find_one(
            User.id == PydanticObjectId(user_id)
        )

        if not user:
            raise not_found_exception()

        new_password = self.hash_service.hash(req.password)

        await user.update(
            {"$set": {"password_hash": new_password}}
            )       
        
        return {"message":"password updated"}

    async def update_bio(
        self,
        req: Bio_req,
        current_user: Token_payload
    ):
            result = await User.find(
                User.id == PydanticObjectId(current_user.id)
            ).update(
                {"$set": {"bio": req.bio}}
            )

            if result.matched_count == 0:
                raise not_found_exception("User not found")

            return {"message": "bio updated"}     
        
    
    async def get_me(
            self,
            current_user:Token_payload
    ) -> Me_res:
        user_db = await User.find_one(User.id == PydanticObjectId(current_user.id))
        if not user_db:
            raise not_found_exception()
        res = Me_res(
            **user_db.model_dump()
        )
        return res
    
    async def delete_user(
            self,
            req:User_id_req,
            current_user:Token_payload
    ):
        if current_user.role != User_role.ADMIN:
            raise forbidden_exception()
        
        if current_user.id == str(req.id):
            raise bad_request_exception("you can not delete your account")
        
        user_db = await User.find_one(User.id == PydanticObjectId(req.id))
        if not user_db:
            raise not_found_exception()
        
        await user_db.delete()

        return{
            "message":f"{req.id} is deleted"
        }

    async def search_users(self, req: str ,current_user:Token_payload):
        users = await (
            User.find(
                User.id != PydanticObjectId(current_user.id),
                {
                    "user_name": {
                        "$regex": f"^{req}",
                        "$options": "i",
                    },
                }
            )
            .limit(5)
            .to_list()
        )

        return [
            User_res.model_validate(user)
            for user in users
        ]
