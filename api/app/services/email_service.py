from pydantic import EmailStr
from redis.asyncio import Redis
import json

class Email_service():
    def __init__(
        self,
        redis_client : Redis
    ):
        self.redis_client = redis_client

    async def _push_job(self, job : dict):
        #push job to redis queue
        await self.redis_client.rpush(
            "email_queue",
            json.dumps(job)
        )
        
    async def send_registration_otp(
            self,
            email:str,
            otp:str,
            ex:str
        ):

        job = {
            "type": "registration_otp",
            "email": email,
            "otp": otp,
            "ex":ex
        }
        await self._push_job(job=job)

    async def send_forgot_password_otp(
            self,
            email:str,
            user_name:str,
            otp:str,
            ex:str
        ):

        job = {
            "type": "forgot_password_otp",
            "email": email,
            "user_name":user_name,
            "otp": otp,
            "ex":ex
        }
        await self._push_job(job=job)

    async def send_account_created(
            self,
            email:str,
            user_name:str
        ):

        job = {
            "type": "account_created",
            "email": email,
            "user_name":user_name
        }
        await self._push_job(job=job)



