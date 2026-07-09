from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import retrieve_rag
from app.services.slot_service import get_slot_context, get_chat_history, save_chat_history
from app.services.llm_service import call_qwen

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/chat")
async def chat(request: ChatRequest):
    rag_context = retrieve_rag(request.message)
    slot_context = get_slot_context(request.user_id)
    history = get_chat_history(request.user_id)
    response = await call_qwen(request.message, slot_context, rag_context, history)

    save_chat_history(request.user_id, request.message, response)

    return {"response": response}


@router.get("/chat/history/{user_id}")
async def chat_history(user_id: str):
    history = get_chat_history(user_id)
    return {"history": history}