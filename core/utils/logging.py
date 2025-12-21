"""
Logging van responses voor analyse.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict

LOG_FILE = "model_responses_log.json"


def log_response(
    model_id: str,
    model_info: str,
    agent_naam: str,
    vraag: str,
    antwoord: str,
    stelling: str = "",
    bronnen: Optional[List[Dict]] = None
) -> None:
    """Logt een response naar JSON bestand."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "stelling": stelling,
        "model_id": model_id,
        "model_info": model_info,
        "agent": agent_naam,
        "vraag": vraag,
        "antwoord": antwoord
    }
    
    if bronnen:
        log_entry["bronnen"] = bronnen
    
    try:
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log_data = []
    
    log_data.append(log_entry)
    
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def lees_log() -> Optional[str]:
    """Leest het log bestand als string."""
    try:
        with open(LOG_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
