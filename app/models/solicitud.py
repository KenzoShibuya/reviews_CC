from pydantic import BaseModel
from typing import Literal

class SolicitudCreate(BaseModel):
    book_id: int
    seller_id: int
    initial_message: str

class MessageCreate(BaseModel):
    text: str

class StatusUpdate(BaseModel):
    status: Literal["pendiente", "aceptada", "rechazada", "cancelada"]
