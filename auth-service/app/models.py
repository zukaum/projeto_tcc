from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserOut(BaseModel):
    email: EmailStr
    role: str
    verified: bool
