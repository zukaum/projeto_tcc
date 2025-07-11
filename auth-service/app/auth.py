from fastapi import HTTPException
from passlib.hash import bcrypt
from jose import jwt
from .config import JWT_SECRET
from datetime import datetime, timedelta

def hash_password(password: str):
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str):
    return bcrypt.verify(password, hashed)

def create_token(data: dict, expires_minutes: int = 60*24):
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(minutes=expires_minutes)})
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
