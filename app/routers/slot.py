from fastapi import APIRouter
from pydantic import BaseModel
from app.services.slot_service import get_all_slots, update_slot_config

router = APIRouter()

@router.get("/slots/{user_id}")
async def get_slots(user_id: str):
    slots = get_all_slots(user_id)
    return {"slots": slots}


class SlotConfigRequest(BaseModel):
    medicine_name: str

@router.put("/slots/{slot_id}/config")
async def config_slot(slot_id: str, request: SlotConfigRequest):
    update_slot_config(slot_id, request.medicine_name)
    return {"status": "ok"}
