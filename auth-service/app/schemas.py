from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import date
from typing import Optional

class UserRole(str, Enum):
    usuario_fisico = "usuário físico"
    auditor = "auditor"
    cartorio = "cartório"

class UserCreate(BaseModel):
    id: str = Field(..., description="Identificador único do usuário")
    nome_completo: str = Field(..., description="Nome completo do usuário")
    email: EmailStr
    password: str
    role: UserRole
    data_nascimento: date

class UserBase(BaseModel):
    nome_completo: str
    id_documento: str
    email: str
    role: str
    data_nascimento: date

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    id_documento: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    data_nascimento: Optional[date] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    uuid: str

    class Config:
        orm_mode = True
