from fastapi import FastAPI
from app.routers.chat import router as chat_router
from app.routers.sensor import router as sensor_router
from app.routers.slot import router as slot_router
from app.routers.auth import router as auth_router

app = FastAPI(title="MediBox AI Backend")
app.include_router(chat_router)
app.include_router(sensor_router)
app.include_router(slot_router)
app.include_router(auth_router)

@app.get("/")
def root():

    return {"status": "MediBox AI is running"}