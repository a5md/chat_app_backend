from passlib.context import CryptContext
import hashlib
import hmac


class Hash_service:

    def __init__(self):
        self._pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto"
        )

    # Password hashing
    def hash(self, password: str) -> str:
        return self._pwd_context.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return self._pwd_context.verify(
            password,
            password_hash
        )

    # Refresh token hashing
    def hash_token(self, token: str) -> str:
        return hashlib.sha256(
            token.encode()
        ).hexdigest()

    def verify_token(self, token: str, token_hash: str) -> bool:
        return hmac.compare_digest(
            self.hash_token(token),
            token_hash
        )