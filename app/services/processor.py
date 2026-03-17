import json
from app.services.telegram import send_telegram


def process_alert(data: dict):
    message = json.dumps(data, indent=2)
    send_telegram(message)
