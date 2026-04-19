import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import JWT_SECRET

security = HTTPBearer()

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
