from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/Usuario/login")
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print(f"Token will expire at: {expire}")
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"[DEBUG AUTH] Token Creado. Expiración: {expire.isoformat()}")
    return token

def decode_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEBUG DECODE] Payload decodificado con éxito: {payload}")
        usuario_id: int = payload.get("sub")
        rol_id: int = payload.get("rol_id")
        print(f"[DEBUG DECODE] Extrayendo IDs: usuario_id={usuario_id}, rol_id={rol_id}")
        if usuario_id is None or rol_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        print("[DEBUG DECODE] Éxito: Token válido y con datos esenciales.")
        return {"usuario_id": usuario_id, "rol_id": rol_id}
    except jwt.PyJWTError as e:
        print(f"[DEBUG DECODE] ERROR PyJWTError: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")