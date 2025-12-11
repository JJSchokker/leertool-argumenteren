"""
Context Weaver - bouwt dynamische systeem prompts voor agenten.

De parameters (p_bronnen, p_cv_detail, p_referentie) worden door Python
omgezet naar concrete ja/nee beslissingen. De LLM krijgt alleen duidelijke
instructies, geen kansen om te interpreteren.
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


def kans_naar_beslissing(kans: float) -> bool:
    """
    Zet een kans (0-1) om naar een concrete beslissing (True/False).
    
    Args:
        kans: Waarde tussen 0 en 1
        
    Returns:
        bool: True als de actie moet plaatsvinden
    """
    if kans <= 0:
        return False
    if kans >= 1:
        return True
    return random.random() < kans


def context_weaver(agent: Agent, history: List[Dict]) -> str:
    """
    Bouwt een systeem prompt met dynamische context.
    
    Python beslist op basis van de parameters wat er in de prompt komt.
    De LLM krijgt alleen concrete instructies (wel/niet doen), geen kansen.
    
    Args:
        agent: De agent die spreekt
        history: Gesprekhistorie
    
    Returns:
        str: Complete systeem prompt met context
    """
    instructies = [agent.systeem_prompt]
    
    # === KENNISBANK (p_bronnen) ===
    # Python beslist: wel of geen feit meegeven
    if agent.standpunt != "GEEN" and kans_naar_beslissing(agent.p_bronnen):
        # Kies feiten uit de juiste kennisbank
        if agent.standpunt == "PRO":
            kennisbank = KENNIS_PRO
        else:  # CONTRA
            kennisbank = KENNIS_CONTRA
        
        # Hoge p_bronnen (>0.5) = 2 feiten, anders 1
        aantal = 2 if agent.p_bronnen > 0.5 else 1
        feiten = random.sample(kennisbank, min(aantal, len(kennisbank)))
        
        # Duidelijke instructie voor LLM
        instructies.append(f"\nGEBRUIK DIT FEIT IN JE ANTWOORD: {feiten[0]}")
        if len(feiten) > 1:
            instructies.append(f"OF DIT FEIT: {feiten[1]}")
    
    # === CV DETAILS (p_cv_detail) ===
    # Python beslist: wel of geen persoonlijk detail
    cv = CV_DATA.get(agent.naam, "")
    if cv and kans_naar_beslissing(agent.p_cv_detail):
        instructies.append(f"\nVERWERK DIT PERSOONLIJKE DETAIL IN JE ANTWOORD: {cv}")
    
    # === AFLEIDERS (speciale agenten) ===
    # Peter Mercier: F1 obsessie
    if agent.naam == "Peter Mercier" and kans_naar_beslissing(0.7):
        feit = random.choice(MAX_VERSTAPPEN_FEITEN)
        instructies.append(f"\nJE MOET DIT F1-FEIT NOEMEN: {feit}")
    
    # Jessica Stekelenburg: Yoga obsessie
    if agent.naam == "Jessica Stekelenburg" and kans_naar_beslissing(0.7):
        feit = random.choice(YOGA_FEITEN)
        instructies.append(f"\nJE MOET DIT YOGA-FEIT NOEMEN: {feit}")
    
    # === REFERENTIE NAAR GESPREK (p_referentie) ===
    # Python beslist: wel of niet terugverwijzen
    user_msgs = [m for m in history if m.get("role") == "user"]
    if len(user_msgs) >= 2 and kans_naar_beslissing(agent.p_referentie):
        instructies.append("\nVERWIJS IN JE ANTWOORD NAAR IETS DAT EERDER IS GEZEGD.")
    
    return "\n".join(instructies)
