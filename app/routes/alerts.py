from fastapi import APIRouter, Request
from app.db import db
from app.config import COLLECTION_NAME
from app.models import format_alert
from app.services.processor import process_alert

router = APIRouter()

@router.post("/webhook")
async def receive_alert(request: Request):
    data = await request.json()
    alert = format_alert(data)
    db[COLLECTION_NAME].insert_one(alert)
    process_alert(data)
    return {"status": "received"}
