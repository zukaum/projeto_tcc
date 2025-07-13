from fastapi import HTTPException
from .schemas import UserIn, UserUpdate, UserRole
from .auth import hash_password
from app.db import db
from uuid import uuid4
import re

def validar_cpf(cpf: str) -> bool:
    return bool(re.fullmatch(r"\d{11}", cpf))

def validar_cnpj(cnpj: str) -> bool:
    return bool(re.fullmatch(r"\d{14}", cnpj))

async def create_user(user: UserIn):
    if user.role == UserRole.usuario_fisico:
        if not validar_cpf(user.id_documento):
            raise HTTPException(status_code=400, detail="CPF inválido (precisa ter 11 dígitos numéricos)")
    else:
        if not validar_cnpj(user.id_documento):
            raise HTTPException(status_code=400, detail="CNPJ inválido (precisa ter 14 dígitos numéricos)")

    user_data = {
        "uuid": str(uuid4()),
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

async def get_user(user_id: str):
    user = await db["users"].find_one({"uuid": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_users(skip: int = 0, limit: int = 100):
    cursor = db["users"].find().skip(skip).limit(limit)
    return [user async for user in cursor]

async def update_user(user_id: str, user_update: UserUpdate):
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")

    result = await db["users"].update_one({"uuid": user_id}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await db["users"].find_one({"uuid": user_id})
    return updated_user

async def delete_user(user_id: str):
    result = await db["users"].delete_one({"uuid": user_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": "User deleted"}
