from fastapi import FastAPI, Depends, Body
from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, DB_NAME, BASE_URL
from .models import UserIn, UserOut
from .auth import hash_password, verify_password, create_token, decode_token
from .email_utils import send_verification_email

app = FastAPI()
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

@app.post("/register")
async def register(user: UserIn):
    if await db.users.find_one({"email": user.email}):
        return {"error": "Usuário já existe"}
    hashed = hash_password(user.password)
    token = create_token({"email": user.email})

    await db.users.insert_one({
        "email": user.email,
        "password": hashed,
        "role": user.role,
        "verified": False,
        "verify_token": token
    })

    link = f"{BASE_URL}/verify/{token}"
    send_verification_email(user.email, link)
    return {"message": "Usuário registrado. Verifique seu e-mail."}

@app.get("/verify/{token}")
async def verify(token: str):
    data = decode_token(token)
    user = await db.users.find_one({"email": data["email"]})
    if not user:
        return {"error": "Usuário não encontrado"}

    await db.users.update_one({"email": user["email"]}, {
        "$set": {"verified": True},
        "$unset": {"verify_token": ""}
    })
    return {"message": "E-mail confirmado."}

@app.post("/login")
async def login(email: str = Body(...), password: str = Body(...)):
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        return {"error": "Credenciais inválidas"}
    if not user["verified"]:
        return {"error": "E-mail não verificado"}

    token = create_token({"id": str(user["_id"]), "role": user["role"]})
    return {"token": token, "role": user["role"]}
