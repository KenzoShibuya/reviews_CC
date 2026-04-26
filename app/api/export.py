from fastapi import APIRouter, Depends
from app.db.mongodb import db
from app.middleware.auth import get_api_key

router = APIRouter(prefix="/api/export", tags=["Ingesta Data Science"])

@router.get("/solicitudes", summary="Extraer 100% de Solicitudes (Para Analytics)")
async def export_solicitudes(api_key: str = Depends(get_api_key)):
    cursor = db.solicitudes_collection.find({})
    solicitudes = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        solicitudes.append(document)
    return solicitudes
