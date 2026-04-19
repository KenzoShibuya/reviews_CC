from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Any
from datetime import datetime, timezone
import jwt
import os
from bson import ObjectId
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env (útil para desarrollo local)
load_dotenv()

# Lee las variables SIN valores por defecto inseguros
MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

# Validación estricta: Si la app arranca sin credenciales, que lance un error inmediatamente
if not MONGO_URL or not JWT_SECRET:
    raise ValueError("ERROR CRÍTICO: Faltan variables de entorno (MONGO_URL o JWT_SECRET)")

app = FastAPI(
    title="MS3 - Reviews y Solicitudes",
    description="Microservicio NoSQL para gestionar reseñas y solicitudes de libros",
    version="1.0.0"
)

security = HTTPBearer()

# --- CONFIGURACIÓN MONGODB ---
client = AsyncIOMotorClient(MONGO_URL)
db = client.reviews_db
reviews_collection = db.reviews
solicitudes_collection = db.solicitudes

# Helper para ObjectId en Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


# --- MODELOS PYDANTIC ---

class ReviewCreate(BaseModel):
    target_user_id: int
    transaction_id: str
    rating: float = Field(..., ge=1, le=5)
    comment: str


class SolicitudCreate(BaseModel):
    book_id: int
    seller_id: int
    initial_message: str


class MessageCreate(BaseModel):
    text: str


class StatusUpdate(BaseModel):
    status: str  # pendiente, aceptada, rechazada, cancelada, entregado, devuelto


# --- MIDDLEWARE DE AUTENTICACIÓN ---

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except ValueError:
        raise HTTPException(status_code=401, detail="Formato de token inválido")


# --- ENDPOINTS REVIEWS ---

@app.post("/api/reviews", tags=["Reviews"])
async def create_review(review: ReviewCreate, user_id: int = Depends(get_current_user_id)):
    try:
        review_doc = review.model_dump()
        review_doc["user_id"] = user_id
        review_doc["created_at"] = datetime.now(timezone.utc)

        result = await reviews_collection.insert_one(review_doc)
        return {"message": "Review creada", "id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error al crear review: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al guardar la review")


@app.get("/api/reviews/user/{user_id}", tags=["Reviews"])
async def get_user_reviews(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    cursor = reviews_collection.find({"target_user_id": user_id})
    reviews = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        reviews.append(document)
    return reviews


@app.get("/api/reviews/stats/{user_id}", tags=["Reviews"])
async def get_user_review_stats(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    pipeline = [
        {"$match": {"target_user_id": user_id}},
        {"$group": {
            "_id": "$target_user_id",
            "average_rating": {"$avg": "$rating"},
            "total_reviews": {"$sum": 1}
        }}
    ]
    cursor = reviews_collection.aggregate(pipeline)
    stats = await cursor.to_list(length=1)

    if stats:
        return stats[0]
    return {"_id": user_id, "average_rating": 0, "total_reviews": 0}


# --- ENDPOINTS SOLICITUDES ---

@app.post("/api/solicitudes", tags=["Solicitudes"])
async def create_solicitud(solicitud: SolicitudCreate, user_id: int = Depends(get_current_user_id)):
    solicitud_doc = {
        "book_id": solicitud.book_id,
        "buyer_id": user_id,
        "seller_id": solicitud.seller_id,
        "status": "pendiente",
        "messages": [{
            "from": user_id,
            "text": solicitud.initial_message,
            "date": datetime.now(timezone.utc)
        }],
        "created_at": datetime.now(timezone.utc)
    }
    result = await solicitudes_collection.insert_one(solicitud_doc)
    return {"message": "Solicitud creada", "id": str(result.inserted_id)}


@app.get("/api/solicitudes/user/{user_id}", tags=["Solicitudes"])
async def get_user_solicitudes(user_id: int, current_user: int = Depends(get_current_user_id)):
    cursor = solicitudes_collection.find({
        "$or": [{"buyer_id": user_id}, {"seller_id": user_id}]
    })
    solicitudes = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        solicitudes.append(document)
    return solicitudes


@app.get("/api/solicitudes/{id}", tags=["Solicitudes"])
async def get_solicitud(id: str, current_user: int = Depends(get_current_user_id)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de solicitud inválido")
    solicitud = await solicitudes_collection.find_one({"_id": ObjectId(id)})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    solicitud["_id"] = str(solicitud["_id"])
    return solicitud


@app.post("/api/solicitudes/{id}/messages", tags=["Solicitudes"])
async def add_message(id: str, msg: MessageCreate, user_id: int = Depends(get_current_user_id)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de solicitud inválido")
    new_message = {
        "from": user_id,
        "text": msg.text,
        "date": datetime.now(timezone.utc)
    }
    result = await solicitudes_collection.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"messages": new_message}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return {"message": "Mensaje añadido con éxito"}


@app.put("/api/solicitudes/{id}/status", tags=["Solicitudes"])
async def update_solicitud_status(id: str, status_update: StatusUpdate, current_user_id: int = Depends(get_current_user_id)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de solicitud inválido")
    result = await solicitudes_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status_update.status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return {"message": f"Estado actualizado a {status_update.status}"}