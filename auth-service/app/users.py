from fastapi import HTTPException
from .schemas import UserCreate, UserRole
from .auth import hash_password
from app.db import db
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
