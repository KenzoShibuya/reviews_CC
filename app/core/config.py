import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

if not MONGO_URL or not JWT_SECRET:
    raise ValueError("ERROR CRÍTICO: Faltan variables de entorno (MONGO_URL o JWT_SECRET)")
