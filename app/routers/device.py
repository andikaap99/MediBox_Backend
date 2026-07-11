from fastapi import APIRouter
from pydantic import BaseModel
from app.services.device_service import get_device_by_user_id, upsert_device, delete_device

router = APIRouter()


class UpsertDeviceRequest(BaseModel):
    mac_address: str
    device_name: str = ""
    user_id: str


@router.get("/device/{user_id}")
async def get_user_device(user_id: str):
    device = get_device_by_user_id(user_id)
    if not device:
        return {"device": None}
    return {"device": device}


@router.post("/device")
async def register_or_update_device(request: UpsertDeviceRequest):
    device = upsert_device(request.user_id, request.mac_address, request.device_name)
    return {"status": "ok", "device": device}


@router.delete("/device/{user_id}")
async def remove_device(user_id: str):
    delete_device(user_id)
    return {"status": "ok"}
