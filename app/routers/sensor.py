from fastapi import APIRouter
from pydantic import BaseModel
from app.services.sensor_service import update_slot_from_sensor

router = APIRouter()

class SensorUpdateRequest(BaseModel):
    user_id: str
    slot_label: str
    is_filled: bool

@router.post("/sensor/update")
async def sensor_update(request: SensorUpdateRequest):
    update_slot_from_sensor(request.user_id, request.slot_label, request.is_filled)
    return {"status": "ok"}
