from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from bson import ObjectId
from app.models.solicitud import SolicitudCreate, MessageCreate, StatusUpdate
from app.db.mongodb import db
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/api/solicitudes", tags=["Solicitudes"])

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
    result = await db.solicitudes_collection.insert_one(solicitud_doc)
    return {"message": "Solicitud creada", "id": str(result.inserted_id)}

@router.get("/user/{user_id}")
async def get_user_solicitudes(user_id: int, current_user: int = Depends(get_current_user_id)):
    # Solo permitimos ver solicitudes si eres el dueño del perfil o el orquestador
    cursor = db.solicitudes_collection.find({
        "$or": [{"buyer_id": user_id}, {"seller_id": user_id}]
    })
    solicitudes = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        solicitudes.append(document)
    return solicitudes

@router.get("/{id}")
async def get_solicitud(id: str, current_user_id: int = Depends(get_current_user_id)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de solicitud inválido")
    
    solicitud = await db.solicitudes_collection.find_one({"_id": ObjectId(id)})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    # Seguridad: Solo el comprador o vendedor pueden ver el detalle
    if current_user_id != solicitud["buyer_id"] and current_user_id != solicitud["seller_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta solicitud")

    solicitud["_id"] = str(solicitud["_id"])
    return solicitud

@router.post("/{id}/messages")
async def add_message(id: str, msg: MessageCreate, user_id: int = Depends(get_current_user_id)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de solicitud inválido")
    
    solicitud = await db.solicitudes_collection.find_one({"_id": ObjectId(id)})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    # Seguridad: Solo participantes pueden enviar mensajes
    if user_id != solicitud["buyer_id"] and user_id != solicitud["seller_id"]:
        raise HTTPException(status_code=403, detail="No eres parte de esta solicitud")

    new_message = {
        "from": user_id,
        "text": msg.text,
        "date": datetime.now(timezone.utc)
    }
    await db.solicitudes_collection.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"messages": new_message}}
    )
    return {"message": "Mensaje añadido con éxito"}

@router.put("/{id}/status")
async def update_solicitud_status(id: str, status_update: StatusUpdate, current_user_id: int = Depends(get_current_user_id)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de solicitud inválido")

    solicitud = await db.solicitudes_collection.find_one({"_id": ObjectId(id)})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    # Seguridad: 
    # - Si es 'cancelada', solo el comprador puede hacerlo.
    # - Si es 'aceptada' o 'rechazada', solo el vendedor puede hacerlo.
    status = status_update.status.lower()
    
    if status == "cancelada" and current_user_id != solicitud["buyer_id"]:
        raise HTTPException(status_code=403, detail="Solo el comprador puede cancelar la solicitud")
    
    if status in ["aceptada", "rechazada"] and current_user_id != solicitud["seller_id"]:
        raise HTTPException(status_code=403, detail="Solo el vendedor puede cambiar este estado")

    await db.solicitudes_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status}}
    )
    return {"message": f"Estado actualizado a {status}"}
