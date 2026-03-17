from datetime import datetime

def format_alert(data: dict):
    return {
        "data": data,
        "created_at": datetime.utcnow()
    }
