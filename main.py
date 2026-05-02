from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import solicitudes, export
from app.db.mongodb import db
from app.core.config import ALLOWED_ORIGINS

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.close()

app = FastAPI(
    title="MS3 - Reviews y Solicitudes",
    description="Microservicio NoSQL para gestionar reseñas y solicitudes de libros",
    version="1.0.0",
    lifespan=lifespan
)

origins = ["*"] if not ALLOWED_ORIGINS else [ALLOWED_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Api-Key"],
)

app.include_router(solicitudes.router)
app.include_router(export.router)

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "MS3 - Reviews y Solicitudes is running",
        "docs": "/docs"
    }
