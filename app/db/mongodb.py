from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URL

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    solicitudes_collection = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(MONGO_URL)
        cls.db = cls.client.solicitudes_db
        cls.solicitudes_collection = cls.db.solicitudes
        print("Conexión a MongoDB establecida")

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            print("Conexión a MongoDB cerrada")

# Objeto global para acceder a las colecciones
db = MongoDB
