from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    usuario_fisico = "usuário físico"
    auditor = "auditor"
    cartorio = "cartório"


class UserIn(BaseModel):
    nome_completo: str
    id_documento: str
    email: EmailStr
    password: str
    role: UserRole
    data_nascimento: date


class UserOut(BaseModel):
    id: str
    nome_completo: str
    id_documento: str
    email: EmailStr
    role: UserRole
    data_nascimento: str  # opcionalmente `date`, mas geralmente convertemos para str ao sair


class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    id_documento: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    data_nascimento: Optional[date] = None
    password: Optional[str] = None