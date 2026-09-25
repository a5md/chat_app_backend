from pydantic import Field
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone
from beanie import Document
from pymongo import IndexModel


class ConversationUser(BaseModel):
    id: str
    user_name: str
    avatar: str | None = None


class Conversation(Document):
    members : List[str] = Field(min_length=2 , max_length=2)
    users: list[ConversationUser] = Field(
        min_length=2,
        max_length=2
    )
    last_message : str | None = Field(default=None , max_length=500)
    last_message_at : datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    class Settings:
        name = "conversations"

        indexes = [
            IndexModel(
                [("members", 1)]
            ),
            IndexModel(
                [
                    ("members", 1),
                    ("last_message_at", -1)
                ]
            ),
        ]