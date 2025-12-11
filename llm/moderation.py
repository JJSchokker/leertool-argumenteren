"""
Vangrail voor het filteren van ongepaste input.
Gebruikt Claude Haiku voor snelle checks.
"""


def check_veiligheid(vangrail_client, tekst: str) -> bool:
    """
    Controleert of input ongepast is voor basisschoolleerlingen.
    
    Args:
        vangrail_client: Anthropic client voor Haiku
        tekst: Te controleren tekst
    
    Returns:
        bool: True als de tekst ongepast is
    """
    if not vangrail_client:
        return False
    
    prompt = f'''UNSAFE = echte scheldwoorden, obsceen taalgebruik, beledigingen.
SAFE = tikfouten, vreemde zinnen, normale vragen. Bij twijfel: SAFE
Tekst: "{tekst}"
Antwoord alleen: UNSAFE of SAFE'''
    
    try:
        response = vangrail_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )
        return "UNSAFE" in response.content[0].text.upper()
    except Exception:
        return False
