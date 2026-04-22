from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from app.models.solicitud import SolicitudCreate, MessageCreate, StatusUpdate
from app.db.mongodb import solicitudes_collection
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/api/solicitudes", tags=["Solicitudes"])

@router.get("")
async def find_solicitudes(
    book_id: Optional[int] = Query(None),
    buyer_id: Optional[int] = Query(None),
    seller_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: int = Depends(get_current_user_id),
):
    query = {}
    if book_id is not None:
        query["book_id"] = book_id
    if buyer_id is not None:
        query["buyer_id"] = buyer_id
    if seller_id is not None:
        query["seller_id"] = seller_id
    if status:
        query["status"] = status

    cursor = solicitudes_collection.find(query)
    result = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        result.append(doc)
    return result

@router.post("")
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

@router.get("/user/{user_id}")
async def get_user_solicitudes(user_id: int, current_user: int = Depends(get_current_user_id)):
    cursor = solicitudes_collection.find({
        "$or": [{"buyer_id": user_id}, {"seller_id": user_id}]
    })
    solicitudes = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        solicitudes.append(document)
    return solicitudes

@router.get("/{id}")
async def get_solicitud(id: str, current_user: int = Depends(get_current_user_id)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de solicitud inválido")
    solicitud = await solicitudes_collection.find_one({"_id": ObjectId(id)})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    solicitud["_id"] = str(solicitud["_id"])
    return solicitud

@router.post("/{id}/messages")
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

@router.put("/{id}/status")
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
