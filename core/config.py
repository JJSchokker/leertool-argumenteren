"""
Configuratie voor de Leertool Argumenteren
==========================================

Hier stel je de actieve stelling in en de bijbehorende documenten folder.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Stelling:
    """
    Een discussiestelling met metadata.
    
    Attributes:
        id: Unieke identifier (moet overeenkomen met folder in documents/)
        titel: De stelling zoals getoond aan gebruikers
        beschrijving: Korte uitleg voor de docent/beheerder
        context: Extra context voor de agents over het onderwerp
    """
    id: str
    titel: str
    beschrijving: str
    context: str


# =============================================================================
# BESCHIKBARE STELLINGEN
# =============================================================================

STELLINGEN = {
    "elektrische_autos": Stelling(
        id="elektrische_autos",
        titel="Elektrisch rijden is goed voor het milieu",
        beschrijving="Discussie over de voor- en nadelen van elektrische auto's voor het milieu",
        context="""Dit gaat over elektrische auto's (EV's) versus benzine/diesel auto's.
Belangrijke onderwerpen: CO2-uitstoot, batterijproductie, stroomnet, laden, 
bereik, kosten, grondstoffen (lithium, kobalt), en de energietransitie."""
    ),
    
    "social_media": Stelling(
        id="social_media",
        titel="Social media is slecht voor jongeren",
        beschrijving="Discussie over de invloed van social media op jongeren",
        context="""Dit gaat over platforms zoals TikTok, Instagram, Snapchat.
Belangrijke onderwerpen: schermtijd, mentale gezondheid, cyberpesten, 
FOMO, privacy, algoritmes, en online veiligheid."""
    ),
    
    "huiswerk": Stelling(
        id="huiswerk",
        titel="Huiswerk moet worden afgeschaft",
        beschrijving="Discussie over nut en noodzaak van huiswerk",
        context="""Dit gaat over huiswerk op de basisschool en middelbare school.
Belangrijke onderwerpen: leerprestaties, stress, vrije tijd, 
zelfstandigheid, ongelijkheid (thuissituatie), en motivatie."""
    ),
}


# =============================================================================
# ACTIEVE STELLING
# =============================================================================

# Verander dit om een andere stelling te activeren
ACTIEVE_STELLING_ID = "elektrische_autos"

def get_actieve_stelling() -> Stelling:
    """Haalt de actief geconfigureerde stelling op."""
    return STELLINGEN[ACTIEVE_STELLING_ID]


def get_stelling_by_id(stelling_id: str) -> Optional[Stelling]:
    """Haalt een specifieke stelling op."""
    return STELLINGEN.get(stelling_id)


def get_alle_stellingen() -> dict:
    """Geeft alle beschikbare stellingen."""
    return STELLINGEN
