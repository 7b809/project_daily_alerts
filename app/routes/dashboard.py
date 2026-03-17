from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.db import db
from app.config import COLLECTION_NAME

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def dashboard(request: Request):
    alerts = list(db[COLLECTION_NAME].find().sort("_id", -1).limit(50))
    return templates.TemplateResponse("index.html", {"request": request, "alerts": alerts})

@router.get("/api/alerts")
async def get_alerts():
    alerts = list(db[COLLECTION_NAME].find().sort("_id", -1).limit(50))
    for a in alerts:
        a["_id"] = str(a["_id"])
    return alerts
