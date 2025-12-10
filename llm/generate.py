"""
Response generatie voor 4 LLM providers.
"""

from typing import List, Dict


def genereer_response(
    clients: dict,
    model_id: str, 
    systeem_prompt: str, 
    messages: List[Dict]
) -> str:
    """
    Genereert een response met het geselecteerde model.
    
    Args:
        clients: Dict met geïnitialiseerde clients
        model_id: ID van het te gebruiken model
        systeem_prompt: Systeem instructies voor het model
        messages: Gesprekhistorie
    
    Returns:
        str: De gegenereerde response
    """
    if model_id not in clients:
        return f"[Model {model_id} niet beschikbaar]"
    
    client_info = clients[model_id]
    provider = client_info["provider"]
    
    try:
        if provider == "anthropic":
            response = client_info["client"].messages.create(
                model=client_info["model_name"],
                max_tokens=300,
                system=systeem_prompt,
                messages=messages
            )
            return response.content[0].text
            
        elif provider == "openai":
            openai_msgs = [{"role": "system", "content": systeem_prompt}] + messages
            response = client_info["client"].chat.completions.create(
                model=client_info["model_name"],
                max_completion_tokens=300,
                messages=openai_msgs
            )
            return response.choices[0].message.content
            
        elif provider == "mistral":
            mistral_msgs = [{"role": "system", "content": systeem_prompt}] + messages
            response = client_info["client"].chat.complete(
                model=client_info["model_name"],
                messages=mistral_msgs
            )
            return response.choices[0].message.content
            
        elif provider == "google":
            conv = f"Instructie: {systeem_prompt}\n\n"
            for msg in messages:
                role = "Gebruiker" if msg["role"] == "user" else "Assistent"
                conv += f"{role}: {msg['content']}\n"
            response = client_info["client"].generate_content(conv)
            return response.text
        
        else:
            return "[Onbekende provider]"
            
    except Exception as e:
        return f"[Fout: {e}]"


def vraag_uitleg(
    clients: dict,
    model_id: str, 
    tekst: str
) -> str:
    """
    Vraagt uitleg over een tekst (voor de hulpfunctie).
    """
    if model_id not in clients:
        return "Selecteer eerst een model."
    
    client_info = clients[model_id]
    systeem = "Je bent discussieleider voor groep 7/8. Leg kort uit (max 3 zinnen) wat de spreker bedoelt of probeert te doen."
    vraag = f"Leg uit: '{tekst}'"
    
    try:
        if client_info["provider"] == "anthropic":
            response = client_info["client"].messages.create(
                model=client_info["model_name"],
                max_tokens=200,
                system=systeem,
                messages=[{"role": "user", "content": vraag}]
            )
            return response.content[0].text
            
        elif client_info["provider"] == "openai":
            response = client_info["client"].chat.completions.create(
                model=client_info["model_name"],
                max_completion_tokens=200,
                messages=[
                    {"role": "system", "content": systeem},
                    {"role": "user", "content": vraag}
                ]
            )
            return response.choices[0].message.content
            
        elif client_info["provider"] == "mistral":
            response = client_info["client"].chat.complete(
                model=client_info["model_name"],
                messages=[
                    {"role": "system", "content": systeem},
                    {"role": "user", "content": vraag}
                ]
            )
            return response.choices[0].message.content
            
        elif client_info["provider"] == "google":
            response = client_info["client"].generate_content(f"{systeem}\n\n{vraag}")
            return response.text
            
    except Exception as e:
        return f"Fout: {e}"
    
    return "Kan niet uitleggen."
