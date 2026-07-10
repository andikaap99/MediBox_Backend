from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sensor_service import update_slot_from_sensor
from app.services.device_service import get_user_id_by_mac

router = APIRouter()

class SensorUpdateRequest(BaseModel):
    mac_address: str
    slot_label: str
    is_filled: bool

@router.post("/sensor/update")
async def sensor_update(request: SensorUpdateRequest):
    user_id = get_user_id_by_mac(request.mac_address)
    if not user_id:
        raise HTTPException(status_code=404, detail="Device not registered")
    update_slot_from_sensor(user_id, request.slot_label, request.is_filled)
    return {"status": "ok"}
