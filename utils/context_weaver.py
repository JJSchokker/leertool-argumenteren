"""
Context Weaver - bouwt dynamische systeem prompts voor agenten.
"""

import random
from typing import List, Dict

from agents import (
    Agent,
    CV_DATA,
    KENNIS_PRO,
    KENNIS_CONTRA,
    MAX_VERSTAPPEN_FEITEN,
    YOGA_FEITEN,
)


def context_weaver(agent: Agent, history: List[Dict]) -> str:
    """
    Bouwt een systeem prompt met dynamische context.
    
    Voegt toe op basis van agent parameters:
    - Feiten uit kennisbank (PRO of CONTRA)
    - Persoonlijke CV details
    - Referenties naar eerder gesprek
    - Speciale content voor afleiders (F1, Yoga)
    
    Args:
        agent: De agent die spreekt
        history: Gesprekhistorie
    
    Returns:
        str: Complete systeem prompt met context
    """
    instructies = [agent.systeem_prompt]
    
    # Kennis uit centrale kennisbank toevoegen (op basis van p_bronnen)
    if agent.standpunt != "GEEN" and random.random() < agent.p_bronnen:
        if agent.standpunt == "PRO":
            aantal = 2 if agent.p_bronnen > 0.5 else 1
            feiten = random.sample(KENNIS_PRO, min(aantal, len(KENNIS_PRO)))
            instructies.append(f"\n→ Gebruik dit feit in je antwoord: {feiten[0]}")
            if len(feiten) > 1:
                instructies.append(f"   Of dit: {feiten[1]}")
        elif agent.standpunt == "CONTRA":
            aantal = 2 if agent.p_bronnen > 0.5 else 1
            feiten = random.sample(KENNIS_CONTRA, min(aantal, len(KENNIS_CONTRA)))
            instructies.append(f"\n→ Gebruik dit feit in je antwoord: {feiten[0]}")
            if len(feiten) > 1:
                instructies.append(f"   Of dit: {feiten[1]}")
    
    # CV detail toevoegen
    cv = CV_DATA.get(agent.naam, "")
    if cv and random.random() < agent.p_cv_detail:
        instructies.append(f"\n→ Verwerk subtiel dit persoonlijke detail: {cv}")
    
    # Speciale content voor afleiders
    if agent.naam == "Peter Mercier" and random.random() < 0.7:
        feit = random.choice(MAX_VERSTAPPEN_FEITEN)
        instructies.append(f"\n→ Probeer dit F1-feit te delen: {feit}")
    
    if agent.naam == "Jessica Stekelenburg" and random.random() < 0.7:
        feit = random.choice(YOGA_FEITEN)
        instructies.append(f"\n→ Probeer dit yoga-feit te delen: {feit}")
    
    # Referentie naar eerder gesprek
    user_msgs = [m for m in history if m.get("role") == "user"]
    if len(user_msgs) >= 2 and random.random() < agent.p_referentie:
        instructies.append("\n→ Verwijs kort naar iets dat eerder in het gesprek is gezegd.")
    
    return "\n".join(instructies)
