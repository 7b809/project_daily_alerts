from fastapi import FastAPI
from app.routes import alerts, dashboard

app = FastAPI()

app.include_router(alerts.router)
app.include_router(dashboard.router)
