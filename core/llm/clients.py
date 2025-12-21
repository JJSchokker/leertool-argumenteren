"""
LLM Client initialisatie voor meerdere providers.
"""

import streamlit as st
from typing import Dict, Optional


def laad_api_keys() -> Dict:
    """
    Laadt API keys uit Streamlit secrets of config.py.
    
    Returns:
        Dict met API configuratie per model
    """
    api_keys = {}
    
    # Probeer Streamlit secrets (voor cloud deployment)
    if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
        for model_id, config in st.secrets['api_keys'].items():
            api_keys[model_id] = dict(config)
        return api_keys
    
    # Fallback naar config.py (voor lokale development)
    try:
        from config import API_KEYS
        return API_KEYS
    except ImportError:
        pass
    
    return api_keys


def initialiseer_clients(api_keys: Dict) -> Dict:
    """
    Initialiseert LLM clients voor alle geconfigureerde providers.
    
    Returns:
        Dict met client info per model_id
    """
    clients = {}
    
    for model_id, config in api_keys.items():
        provider = config.get("provider", "").lower()
        api_key = config.get("api_key", "")
        model_name = config.get("model_name", "")
        
        if not api_key:
            continue
        
        try:
            if provider == "anthropic":
                from anthropic import Anthropic
                clients[model_id] = {
                    "client": Anthropic(api_key=api_key),
                    "provider": provider,
                    "model_name": model_name
                }
            
            elif provider == "openai":
                from openai import OpenAI
                clients[model_id] = {
                    "client": OpenAI(api_key=api_key),
                    "provider": provider,
                    "model_name": model_name
                }
            
            elif provider == "mistral":
                from mistralai import Mistral
                clients[model_id] = {
                    "client": Mistral(api_key=api_key),
                    "provider": provider,
                    "model_name": model_name
                }
            
            elif provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                clients[model_id] = {
                    "client": genai.GenerativeModel(model_name),
                    "provider": provider,
                    "model_name": model_name
                }
        
        except Exception as e:
            print(f"Fout bij initialiseren {model_id}: {e}")
    
    return clients


def maak_vangrail_client(api_keys: Dict) -> Optional[object]:
    """
    Maakt een client voor de vangrail (content moderation).
    Gebruikt Claude Haiku voor snelle checks.
    """
    for model_id, config in api_keys.items():
        if config.get("provider") == "anthropic":
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=config["api_key"])
            except:
                pass
    return None
