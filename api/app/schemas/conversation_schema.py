from pydantic import BaseModel,Field,ConfigDict
from beanie import PydanticObjectId
from typing import List
from datetime import datetime

class Conversation_res(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:PydanticObjectId
    user_name: str
    avatar: str | None = None
    members : List[str] = Field(min_length=2 , max_length=2)
    last_message : str | None = Field(default=None , max_length=500)
    last_message_at : datetime | None = None
    created_at: datetime 

class Conversations_res(BaseModel):
    conversations : List[Conversation_res]
    next_skip : int | None = None

