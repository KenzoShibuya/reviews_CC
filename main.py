from fastapi import FastAPI
from app.api import reviews, solicitudes

app = FastAPI(
    title="MS3 - Reviews y Solicitudes",
    description="Microservicio NoSQL para gestionar reseñas y solicitudes de libros",
    version="1.0.0"
)

# Incluir los routers de cada módulo
app.include_router(reviews.router)
app.include_router(solicitudes.router)

@app.get("/")
async def root():
    return {
        "message": "MS3 - Reviews y Solicitudes is running",
        "docs": "/docs"
    }
