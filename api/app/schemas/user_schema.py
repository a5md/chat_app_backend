from pydantic import BaseModel,EmailStr,Field,field_validator,ConfigDict
from beanie import PydanticObjectId
import re
from datetime import datetime

class User_id_req(BaseModel):
    id:PydanticObjectId

class User_name_schema(BaseModel):
    user_name:str = Field(
        min_length=3,
        max_length=20
    )
    @field_validator("user_name")
    @classmethod
    def validate_username(cls, value: str):
        value = value.lower().strip()
        if not re.match(r"^[a-z0-9_]+$", value):
            raise ValueError(
                "Username can only contain letters, numbers, and underscore"
            )
        return value
    
class Email_schema(BaseModel):
    email : EmailStr
    
class Register_req(User_name_schema,Email_schema):
    password: str = Field(
        min_length=8,
        max_length=128
    )
    
class Verify_otp_req(Email_schema):
    otp : str
    web_client : bool | None = True

class Reset_password_req(BaseModel):
    id:PydanticObjectId | None = None
    password: str = Field(
        min_length=8,
        max_length=128
    )

class Bio_req(BaseModel):
    bio:str = Field(
        min_length=1,
        max_length=500
    )

class Me_res(User_name_schema,Email_schema):
    avatar : str | None = None
    bio : str | None = None
    created_at: datetime

class User_res(User_name_schema):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    avatar : str | None = None
    bio : str | None = None

class Oauth2_register(Email_schema):
    avatar: str | None = None
    sub : str