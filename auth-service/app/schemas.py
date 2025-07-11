from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import date

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