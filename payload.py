import json

def build_payload(symbols: list):
    """
    Returns JSON body required by Groww API
    """
    return json.dumps(symbols)
