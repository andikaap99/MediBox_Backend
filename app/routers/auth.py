from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY
from app.core.auth import hash_password, verify_password, create_access_token

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/register")
async def register(request: RegisterRequest):
    existing = supabase.table("users") \
        .select("id") \
        .eq("email", request.email) \
        .execute()

    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar"
        )

    hashed = hash_password(request.password)
    result = supabase.table("users").insert({
        "email": request.email,
        "password": hashed,
        "full_name": request.full_name
    }).execute()

    user_id = result.data[0]["id"]
    token = create_access_token(user_id)

    return {"access_token": token, "token_type": "bearer", "user_id": user_id}

@router.post("/auth/login")
async def login(request: LoginRequest):
    result = supabase.table("users") \
        .select("id, password") \
        .eq("email", request.email) \
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )

    user = result.data[0]
    if not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )

    token = create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user_id": user["id"]}
