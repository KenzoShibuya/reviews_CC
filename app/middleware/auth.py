import jwt
from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader
from app.core.config import JWT_SECRET, INGESTA_API_KEY

security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except ValueError:
        raise HTTPException(status_code=401, detail="Formato de token inválido")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == INGESTA_API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Acceso denegado: API Key inválida para ingesta")
