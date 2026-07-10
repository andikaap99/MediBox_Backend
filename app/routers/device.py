from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.device_service import get_device, upsert_device, delete_device

router = APIRouter()


class UpsertDeviceRequest(BaseModel):
    mac_address: str
    device_name: str = ""


@router.get("/devices/{user_id}")
async def get_user_device(user_id: str):
    device = get_device(user_id)
    if not device:
        return {"device": None}
    return {"device": device}


@router.post("/devices/{user_id}")
async def register_or_update_device(user_id: str, request: UpsertDeviceRequest):
    device = upsert_device(user_id, request.mac_address, request.device_name)
    return {"status": "ok", "device": device}


@router.delete("/devices/{user_id}")
async def remove_device(user_id: str):
    delete_device(user_id)
    return {"status": "ok"}
