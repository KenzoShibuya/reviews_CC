import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
INGESTA_API_KEY = os.getenv("INGESTA_API_KEY")

if not MONGO_URL or not JWT_SECRET or not INGESTA_API_KEY:
    raise ValueError("ERROR CRÍTICO: Faltan variables de entorno (MONGO_URL, JWT_SECRET o INGESTA_API_KEY)")
