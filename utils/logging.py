"""
Logging van model responses voor analyse.
"""

import json
from datetime import datetime
from typing import Optional

LOG_FILE = "model_responses_log.json"


def log_response(
    api_keys: dict,
    model_id: str, 
    agent_naam: str, 
    vraag: str, 
    antwoord: str
) -> None:
    """
    Logt een response naar JSON bestand voor latere analyse.
    
    Args:
        api_keys: Dict met API configuratie (voor model info)
        model_id: ID van het gebruikte model
        agent_naam: Naam van de agent
        vraag: De gestelde vraag
        antwoord: Het gegenereerde antwoord
    """
    model_info = api_keys.get(model_id, {})
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model_id": model_id,
        "model_info": f"{model_info.get('provider', '?')}/{model_info.get('model_name', '?')}",
        "agent": agent_naam,
        "vraag": vraag,
        "antwoord": antwoord
    }
    
    # Bestaande log laden of nieuwe maken
    try:
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log_data = []
    
    log_data.append(log_entry)
    
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def lees_log() -> Optional[str]:
    """
    Leest het log bestand als string (voor download).
    
    Returns:
        str of None: Log inhoud of None als niet gevonden
    """
    try:
        with open(LOG_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
