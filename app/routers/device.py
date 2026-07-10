from fastapi import APIRouter
from pydantic import BaseModel
from app.services.device_service import get_device_by_mac, upsert_device, delete_device

router = APIRouter()


class UpsertDeviceRequest(BaseModel):
    mac_address: str
    device_name: str = ""
    user_id: str


@router.get("/device/{mac_address}")
async def get_user_device(mac_address: str):
    device = get_device_by_mac(mac_address)
    if not device:
        return {"device": None}
    return {"device": device}


@router.post("/device")
async def register_or_update_device(request: UpsertDeviceRequest):
    device = upsert_device(request.user_id, request.mac_address, request.device_name)
    return {"status": "ok", "device": device}


@router.delete("/device/{mac_address}")
async def remove_device(mac_address: str):
    device = get_device_by_mac(mac_address)
    if device:
        delete_device(device["id"])
    return {"status": "ok"}
