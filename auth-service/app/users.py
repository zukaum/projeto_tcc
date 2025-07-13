from fastapi import HTTPException
from .schemas import UserCreate, UserRole
from .auth import hash_password
from app.db import db
from sqlalchemy.orm import Session
from . import models, schemas
from uuid import uuid4
from passlib.context import CryptContext
import uuid
import re


def validar_cpf(cpf: str) -> bool:
    return bool(re.fullmatch(r"\d{11}", cpf))


def validar_cnpj(cnpj: str) -> bool:
    return bool(re.fullmatch(r"\d{14}", cnpj))


async def create_user(user: UserCreate):
    if user.role == UserRole.usuario_fisico:
        if not validar_cpf(user.id_documento):
            raise HTTPException(status_code=400, detail="CPF inválido (precisa ter 11 dígitos numéricos)")
    else:
        if not validar_cnpj(user.id_documento):
            raise HTTPException(status_code=400, detail="CNPJ inválido (precisa ter 14 dígitos numéricos)")

    user_data = {
        "uuid": str(uuid.uuid4()),
        "nome_completo": user.nome_completo,
        "id_documento": user.id_documento,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "role": user.role,
        "data_nascimento": user.data_nascimento.isoformat()
    }

    await db["users"].insert_one(user_data)
    return user_data["uuid"]


async def get_user_by_uuid(uuid: str):
    user = await db["users"].find_one({"uuid": uuid})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}