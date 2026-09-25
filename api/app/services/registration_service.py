from redis.asyncio import Redis
from fastapi import Response
import json
from beanie.operators import Or,And
from ..schemas.internal.token_schema import Token_payload
from ..services.otp_service import Otp_service
from ..utils.hash_service import Hash_service
from ..services.email_service import Email_service
from ..services.token_service import Token_service
from ..schemas.user_schema import Register_req,Verify_otp_req,Email_schema
from ..models.user import User
from ..core.exceptions import (
    conflict_exception,
    not_found_exception,
    unauthorized_exception
    )


class Registration_service:
    def __init__ (
            self,
            redis_client:Redis,
            otp_service:Otp_service,
            hash_service: Hash_service,
            email_service : Email_service,
            token_service : Token_service
    ):
        self.redis_client = redis_client
        self.otp_service = otp_service
        self.hash_service = hash_service
        self.email_service = email_service
        self.token_service = token_service

    async def register(self, req:Register_req):
        email = req.email.lower().strip()
        user_name = req.user_name
        password_hash = self.hash_service.hash(req.password)
        #find user in mongo
        db_user = await User.find_one(Or(User.email == email , User.user_name == user_name))
        if db_user:
            raise conflict_exception()

        pipe = self.redis_client.pipeline()
        pipe.set(
            f"registration:email:{email}",
            json.dumps({
                "email": email,
                "user_name" : user_name,
                "password_hash": password_hash,
            }),
            ex=600,
            nx=True #add if not exists
        )
        pipe.set(f"registration:user_name:{user_name}",email ,ex=600 , nx=True)
        results = await pipe.execute()

        redis_email, redis_username = results

        if not redis_username:
            raise conflict_exception("Username already pending")

        if not redis_email:
            # release username because email failed
            await self.redis_client.delete(
                f"registration:user_name:{user_name}"
            )
            raise conflict_exception("Email already pending")

        otp = self.otp_service.generate_otp()
        await self.otp_service.store_otp(email=email ,otp=otp)
        await self.email_service.send_registration_otp(email=email, otp=otp ,ex="5")
        return {
        "message": "Verification code sent"
        }

    async def verify_register(self,req:Verify_otp_req,response:Response):
        email = req.email.lower().strip()
        otp = req.otp.strip()

        verify = await self.otp_service.verify_otp(
            otp=otp ,email= email
        )
        if not verify:
            raise conflict_exception("Invalid OTP")

        user_data = await self.redis_client.get(f"registration:email:{email}")
        if not user_data:
            raise not_found_exception()
        
        if isinstance(user_data, bytes):
            user_data = user_data.decode()

        user_data = json.loads(user_data)
        user = User(**user_data)
        await user.insert()

        pipe = self.redis_client.pipeline()
        pipe.delete(f"registration:email:{email}")
        pipe.delete(f"registration:user_name:{user_data['user_name']}")
        await pipe.execute()
        
        await self.email_service.send_account_created(email=user_data["email"],
                                                user_name=user_data['user_name'])

        payload=Token_payload(
            id=str(user.id) ,
            role=user.role,
            is_complete= user.user_name is not None
        )

        return await self.token_service.create_session(
            payload=payload ,response=response ,web_client=req.web_client
        )
    
    async def forgot_password(
            self,
            req:Email_schema
            ):
        #find user by email
        user_email = req.email.strip().lower()
        user_db = await User.find_one(And(User.email == user_email , User.auth.google == None))
        if user_db:
            #send otp
            otp = self.otp_service.generate_otp()
            await self.otp_service.store_otp(
                email=user_email,
                otp=otp
            )
            await self.email_service.send_forgot_password_otp(
                email = user_email,
                user_name=user_db.user_name,
                otp=otp,
                ex="5"
            )

        return {
            "message": "If an account with that email exists, a password reset OTP has been sent."
        }

    async def verify_forgot_password(
            self,
            response: Response,
            req : Verify_otp_req
    ):
        email=req.email.strip().lower()
        verify = await self.otp_service.verify_otp(
            email=email,
            otp= req.otp,
        )
        if verify is False:
            raise unauthorized_exception()
        
        user_db = await User.find_one(User.email == email)
        if not user_db:
            raise not_found_exception("User not found")
        
        payload=Token_payload(
            id=str(user_db.id) ,
            role=user_db.role,
            is_complete=user_db.user_name is not None
        )

        return await self.token_service.create_session(
            payload=payload ,response=response ,web_client=req.web_client
        )




