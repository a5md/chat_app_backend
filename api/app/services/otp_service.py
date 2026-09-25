import secrets
from ..database.redis import redis_client
from ..utils.hash_service import Hash_service


class Otp_service:

    def __init__(
        self,
        hash_service: Hash_service
    ):
        self.hash_service = hash_service
        self.redis_client = redis_client

    def generate_otp(self) -> str:
        return f"{secrets.randbelow(1_000_000):06}"

    async def store_otp(self, email: str, otp: str, ttl: int = 300) -> None:    
                    
            key = f"otp:{email}"
            hashed_otp = self.hash_service.hash(otp)
            pipe = self.redis_client.pipeline() # to send many Redis command in one reqwast
            pipe.hset(
                key,
                mapping={
                    "hash": hashed_otp,
                    "attempts": 0
                }
            )
            pipe.expire(key,ttl)
            await pipe.execute()

    async def get_otp(self, email: str) -> dict:
        key = f"otp:{email}"
        return await self.redis_client.hgetall(key)

    async def delete_otp(self,email: str) -> None:
        key = f"otp:{email}"
        await self.redis_client.delete(key)

    async def verify_otp(self,email: str, otp: str, max_attempts: int = 5) -> bool:

        key = f"otp:{email}"
        stored_otp = await self.redis_client.hgetall(key)

        # OTP does not exist or expired
        if not stored_otp:
            return False
        
        attempts = int(stored_otp.get("attempts", 0))
        # Too many attempts
        if attempts >= max_attempts:
            await self.delete_otp(email)
            return False
        
        valid = self.hash_service.verify(
            otp,
            stored_otp["hash"]
        )
        # Wrong OTP
        if not valid:
            await self.redis_client.hincrby(
                key,
                "attempts",
                1
            )
            return False
        # Correct OTP
        await self.delete_otp(email)
        return True