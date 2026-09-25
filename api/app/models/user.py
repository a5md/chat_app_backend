from pydantic import EmailStr,Field,BaseModel
from typing import Optional
from datetime import datetime,timezone
from beanie import Document
from pymongo import IndexModel
from ..schemas.internal.user_role_schema import User_role

class GoogleAuth(BaseModel):
    sub: str | None = None

class AuthProviders(BaseModel):
    google: GoogleAuth | None = None


class User(Document):
    email: EmailStr
    user_name: Optional[str] = Field(min_length=3, max_length=30)
    role : User_role  = User_role.USER
    avatar : Optional[str] = None
    bio : Optional[str] = Field(default=None, max_length=500)
    password_hash: Optional[str] = None
    auth: AuthProviders =  Field(default_factory=AuthProviders)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    class Settings:
        name = "users"

        indexes = [
            IndexModel(
                [("email", 1)],#indexing on ascending order
                unique=True
            ),
            IndexModel(
                [("user_name", 1)],
                unique=True,
                partialFilterExpression={"user_name": {"$type": "string"}}
            ),
            IndexModel(
                [("auth.google.sub", 1)],
                unique=True,
                partialFilterExpression={"auth.google.sub": {"$type": "string"}}
            )
        ]