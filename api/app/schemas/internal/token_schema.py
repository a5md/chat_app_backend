from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token:str
    token_type:str

class Token_payload(BaseModel):
    id : Optional[str] = None
    role : Optional[str] = None
    is_complete : bool

class Token_req(BaseModel):
    token : str | None = None