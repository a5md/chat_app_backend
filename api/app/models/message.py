from pydantic import Field
from datetime import datetime,timezone
from beanie import Document
from pymongo import IndexModel

class Message(Document):
    sender_id : str
    conversation_id : str
    content : str= Field(min_length=1, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    class Settings:
        name = "messages"

        indexes = [
            IndexModel(
                [("conversation_id", 1),("created_at", -1)]
            ),
            IndexModel(
                [("sender_id", 1)],
            ),
        ]