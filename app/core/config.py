import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ADMIN_KEY = os.getenv("ADMIN_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")

if not MONGO_URL or not JWT_SECRET or not ADMIN_KEY:
    raise ValueError("ERROR CRÍTICO: Faltan variables de entorno (MONGO_URL, JWT_SECRET o ADMIN_KEY)")
