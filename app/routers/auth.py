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

    return {"access_token": token, "token_type": "bearer", "user_id": user_id, "full_name": request.full_name}

@router.post("/auth/login")
async def login(request: LoginRequest):
    result = supabase.table("users") \
        .select("id, password, full_name") \
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
    return {"access_token": token, "token_type": "bearer", "user_id": user["id"], "full_name": user["full_name"]}


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    mac_address: str | None = None
    device_name: str | None = None

@router.put("/auth/profile/{user_id}")
async def update_profile(user_id: str, request: UpdateProfileRequest):
    existing = supabase.table("users") \
        .select("id") \
        .eq("id", user_id) \
        .execute()

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )

    updates = {}
    if request.full_name is not None and request.full_name != "":
        updates["full_name"] = request.full_name
    if request.email is not None and request.email != "":
        email_check = supabase.table("users") \
            .select("id") \
            .eq("email", request.email) \
            .execute()
        if email_check.data and email_check.data[0]["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah digunakan oleh pengguna lain"
            )
        updates["email"] = request.email
    if request.password is not None and request.password != "":
        updates["password"] = hash_password(request.password)
    if request.mac_address is not None and request.mac_address != "":
        updates["mac_address"] = request.mac_address.upper().strip()
    if request.device_name is not None and request.device_name != "":
        updates["device_name"] = request.device_name

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak ada data yang diperbarui"
        )

    supabase.table("users").update(updates).eq("id", user_id).execute()

    updated = supabase.table("users") \
        .select("id, email, full_name, mac_address, device_name") \
        .eq("id", user_id) \
        .execute()

    if not updated.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memperbarui profil"
        )

    return {"status": "ok", "updated": updated.data[0]}
