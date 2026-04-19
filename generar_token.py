import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env (útil para desarrollo local)
load_dotenv()

# Lee la variable JWT_SECRET desde el entorno o .env
JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise ValueError("ERROR CRÍTICO: La variable de entorno JWT_SECRET no está configurada. Asegúrate de tenerla en tu .env o exportada.")

# Simulamos que somos el usuario con ID 1 y creamos un token con expiración de 1 día
user_id_for_test = 1
expiration_time = datetime.utcnow() + timedelta(days=1)
payload = {"user_id": user_id_for_test, "exp": expiration_time}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

print("\n----------------------------------------------------")
print(f" TOKEN JWT GENERADO para user_id={user_id_for_test} ")
print("----------------------------------------------------")
print(f"Copia este texto para el header 'Authorization':\n")
print(f"Bearer {token}")
print("\n----------------------------------------------------")
print(f"El token expirará en: {expiration_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("----------------------------------------------------")