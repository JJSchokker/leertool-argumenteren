"""
Discussiemeester Module
=======================

Helpt leerlingen met:
1. Uitleg vragen (op 3 niveaus: groep 6, 7, 8)
2. Bronnen vragen
"""

from typing import Optional

# AVI-niveau richtlijnen per groep
NIVEAU_INSTRUCTIES = {
    "groep_6": """
SCHRIJF VOOR GROEP 6 (AVI-M6/E6):
- Gebruik KORTE zinnen (maximaal 8-10 woorden per zin)
- Gebruik EENVOUDIGE woorden die een 9-jarige kent
- Leg moeilijke woorden direct uit tussen haakjes
- Gebruik voorbeelden uit het dagelijks leven
- Maximaal 3-4 zinnen totaal
""",
    
    "groep_7": """
SCHRIJF VOOR GROEP 7 (AVI-M7/E7):
- Gebruik zinnen van maximaal 12-15 woorden
- Je mag verbindingswoorden gebruiken zoals 'omdat', 'doordat', 'waardoor'
- Leg vakwoorden uit als je ze gebruikt
- Maximaal 4-5 zinnen totaal
""",
    
    "groep_8": """
SCHRIJF VOOR GROEP 8 (AVI-Plus):
- Je mag langere zinnen gebruiken (15-20 woorden)
- Je mag complexere verbanden leggen
- Vakwoorden mogen, maar geef korte uitleg erbij
- Maximaal 5-6 zinnen totaal
"""
}


NIVEAU_LABELS = {
    "groep_6": "Groep 6",
    "groep_7": "Groep 7",
    "groep_8": "Groep 8"
}


def maak_uitleg_prompt(tekst: str, niveau: str) -> str:
    """Maakt een prompt voor uitleg op een bepaald niveau."""
    niveau_instructie = NIVEAU_INSTRUCTIES.get(niveau, NIVEAU_INSTRUCTIES["groep_7"])
    
    return f"""Je bent een vriendelijke leraar die iets uitlegt aan een leerling.

{niveau_instructie}

DE TEKST DIE JE MOET UITLEGGEN:
"{tekst}"

OPDRACHT:
Leg uit wat deze tekst betekent. Focus op:
- Wat wordt er gezegd?
- Wat bedoelt de spreker?
- Is dit een feit of een mening?

Begin DIRECT met je uitleg, geen inleiding. Nederlands."""


def format_bron_resultaat(bron_info: Optional[str], tekst: str) -> str:
    """Formatteert het bronresultaat voor weergave."""
    if bron_info:
        return f"""📚 **Bron gevonden!**

{bron_info}

---
*Deze informatie komt uit onze bronnendatabase.*"""
    
    return """❓ **Geen exacte bron gevonden**

Deze tekst staat niet in onze bronnendatabase. Dit kan betekenen:
- De spreker gebruikt eigen woorden
- De informatie komt uit een andere bron
- Het is een mening, geen feit

💡 **Tip:** Vraag de spreker waar hij/zij dit heeft gehoord!"""
