from pydantic import Field ,BaseModel
from typing import List
from beanie import PydanticObjectId
from datetime import datetime

class Message_req(BaseModel):
    conversation_id : PydanticObjectId
    content : str= Field(min_length=1, max_length=500)

class Message_res(BaseModel):
    id:PydanticObjectId
    conversation_id : PydanticObjectId
    content : str= Field(min_length=1, max_length=500)
    sender_id : PydanticObjectId
    created_at: datetime

class Messages_res(BaseModel):
    messages : List[Message_res]
    next_oldest : datetime | None = None