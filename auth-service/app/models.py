from pydantic import BaseModel, EmailStr
from datetime import date
from .schemas import UserRole

class UserIn(BaseModel):
    nome_completo: str
    id_documento: str
    email: EmailStr
    password: str
    role: UserRole
    data_nascimento: date

class UserOut(BaseModel):
    email: EmailStr
    role: str
    verified: bool
