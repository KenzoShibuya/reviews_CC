from pydantic import BaseModel

class SolicitudCreate(BaseModel):
    book_id: int
    seller_id: int
    initial_message: str

class MessageCreate(BaseModel):
    text: str

class StatusUpdate(BaseModel):
    status: str  # pendiente, aceptada, rechazada, cancelada, entregado, devuelto
