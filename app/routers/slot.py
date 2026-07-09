from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.slot_service import get_all_slots, add_slot, update_slot_config

router = APIRouter()

@router.get("/slots/{user_id}")
async def get_slots(user_id: str):
    slots = get_all_slots(user_id)
    return {"slots": slots}


class AddSlotRequest(BaseModel):
    slot_label: str
    medicine_name: str = ""

@router.post("/slots/{user_id}")
async def add_new_slot(user_id: str, request: AddSlotRequest):
    try:
        slot = add_slot(user_id, request.slot_label, request.medicine_name)
        return {"status": "ok", "slot": slot}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class SlotConfigRequest(BaseModel):
    medicine_name: str

@router.put("/slots/{slot_id}/config")
async def config_slot(slot_id: str, request: SlotConfigRequest):
    update_slot_config(slot_id, request.medicine_name)
    return {"status": "ok"}
