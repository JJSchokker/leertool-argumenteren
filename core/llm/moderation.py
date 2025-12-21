"""
Content moderation (vangrail) voor veiligheid.
"""

from typing import Optional


def check_veiligheid(vangrail_client: Optional[object], tekst: str) -> bool:
    """
    Checkt of tekst ongepast is (scheldwoorden, etc).
    
    Returns:
        True als tekst ONVEILIG is, False als veilig
    """
    if not vangrail_client or not tekst.strip():
        return False
    
    try:
        response = vangrail_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": f"""Bevat deze tekst scheldwoorden, beledigingen of ongepaste taal voor kinderen?
Antwoord alleen JA of NEE.

Tekst: "{tekst}"
"""
            }]
        )
        
        antwoord = response.content[0].text.strip().upper()
        return "JA" in antwoord
    
    except Exception:
        return False
