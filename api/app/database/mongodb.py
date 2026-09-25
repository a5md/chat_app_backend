from pymongo import AsyncMongoClient
from ..models.user import User
from ..models.message import Message
from ..models.conversation import Conversation
from beanie import init_beanie
from ..core.config import settings


client = AsyncMongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DATABASE]

async def init_db():
    await init_beanie(
        database=db,
        document_models=[
            User,
            Message,
            Conversation
        ]
    )

async def close_db():
    client.close()

