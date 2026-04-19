from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client.reviews_db
reviews_collection = db.reviews
solicitudes_collection = db.solicitudes
