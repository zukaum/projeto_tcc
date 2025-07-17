from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId
from datetime import date
from .database import db
from .schemas import UserIn, UserOut, UserUpdate
from .config import BASE_URL
from .auth import hash_password, verify_password, create_token, decode_token
from .email_utils import send_verification_email


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register(user: UserIn):
    if await db["users"].find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Usuário já existe")

    hashed = hash_password(user.password)
    token = create_token({"email": user.email})

    result = await db["users"].insert_one({
        "nome_completo": user.nome_completo,
        "id_documento": user.id_documento,
        "email": user.email,
        "password": hashed,
        "role": user.role.value,
        "data_nascimento": str(user.data_nascimento),
        "verified": False,
        "verify_token": token
    })

    link = f"{BASE_URL}/verify/{token}"
    send_verification_email(user.email, link)
    return {"message": "Usuário registrado. Verifique seu e-mail.", "id": str(result.inserted_id)}


@app.get("/verify/{token}")
async def verify(token: str):
    data = decode_token(token)
    user = await db["users"].find_one({"email": data["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    await db["users"].update_one({"email": user["email"]}, {
        "$set": {"verified": True},
        "$unset": {"verify_token": ""}
    })
    return {"message": "E-mail confirmado."}


@app.post("/login")
async def login(email: str = Body(...), password: str = Body(...)):
    user = await db["users"].find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not user["verified"]:
        raise HTTPException(status_code=403, detail="E-mail não verificado")

    token = create_token({"id": str(user["_id"]), "role": user["role"]})
    return {"token": token, "role": user["role"]}


@app.get("/users", response_model=List[UserOut])
async def read_users(skip: int = 0, limit: int = 100):
    cursor = db["users"].find().skip(skip).limit(limit)
    users_list = []
    async for user in cursor:
        users_list.append(UserOut(
            id=str(user["_id"]),
            nome_completo=user["nome_completo"],
            id_documento=user["id_documento"],
            email=user["email"],
            role=user["role"],
            data_nascimento=date.fromisoformat(user["data_nascimento"])
        ))
    return users_list


@app.get("/users/{user_id}", response_model=UserOut)
async def read_user(user_id: str):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return UserOut(
        id=str(user["_id"]),
        nome_completo=user["nome_completo"],
        id_documento=user["id_documento"],
        email=user["email"],
        role=user["role"],
        data_nascimento=date.fromisoformat(user["data_nascimento"])
    )


@app.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: str, user_update: UserUpdate):
    update_data = {
        k: (v.isoformat() if isinstance(v, date) else v)
        for k, v in user_update.dict().items()
        if v is not None
    }

    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    return UserOut(
        id=str(user["_id"]),
        nome_completo=user["nome_completo"],
        id_documento=user["id_documento"],
        email=user["email"],
        role=user["role"],
        data_nascimento=date.fromisoformat(user["data_nascimento"])
    )


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário deletado"}