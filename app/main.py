from fastapi import FastAPI
from app.routers.chat import router as chat_router

app = FastAPI(title="MediBox AI Backend")
app.include_router(chat_router)

@app.get("/")
def root():
    
    return {"status": "MediBox AI is running"}