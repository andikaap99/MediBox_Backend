from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import retrieve_rag
from app.services.slot_service import get_slot_context
from app.services.llm_service import call_qwen

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/chat")
async def chat(request: ChatRequest):
    rag_context = retrieve_rag(request.message)
    slot_context = get_slot_context(request.user_id)
    response = await call_qwen(request.message, slot_context, rag_context)
    
    return {"response": response}