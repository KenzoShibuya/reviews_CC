from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import reviews, solicitudes, export
from app.db.mongodb import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de encendido
    await db.connect()
    yield
    # Lógica de apagado
    await db.close()

app = FastAPI(
    title="MS3 - Reviews y Solicitudes",
    description="Microservicio NoSQL para gestionar reseñas y solicitudes de libros",
    version="1.0.0",
    lifespan=lifespan
)

# Incluir los routers
app.include_router(reviews.router)
app.include_router(solicitudes.router)
app.include_router(export.router)

@app.get("/")
async def root():
    return {
        "message": "MS3 - Reviews y Solicitudes is running",
        "docs": "/docs"
    }
