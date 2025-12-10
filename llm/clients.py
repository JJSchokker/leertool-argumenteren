"""
LLM client initialisatie voor meerdere providers.
"""

import streamlit as st
from anthropic import Anthropic

# Optionele providers
try:
    from openai import OpenAI
    OPENAI_BESCHIKBAAR = True
except ImportError:
    OPENAI_BESCHIKBAAR = False

try:
    from mistralai import Mistral
    MISTRAL_BESCHIKBAAR = True
except ImportError:
    MISTRAL_BESCHIKBAAR = False

try:
    import google.generativeai as genai
    GOOGLE_BESCHIKBAAR = True
except ImportError:
    GOOGLE_BESCHIKBAAR = False


def laad_api_keys():
    """
    Laadt API keys uit Streamlit secrets (online) of config.py (lokaal).
    """
    # Probeer Streamlit secrets (voor Cloud deployment)
    if hasattr(st, 'secrets'):
        try:
            if 'api_keys' in st.secrets:
                api_keys = {}
                for model_id in ['model_1', 'model_2', 'model_3', 'model_4']:
                    if model_id in st.secrets.api_keys:
                        api_keys[model_id] = dict(st.secrets.api_keys[model_id])
                if api_keys:
                    return api_keys
        except Exception:
            pass
    
    # Fallback naar lokale config.py
    try:
        from config import API_KEYS
        return API_KEYS
    except ImportError:
        st.error("❌ Geen API keys gevonden! Maak config.py aan of configureer Streamlit secrets.")
        st.stop()


def initialiseer_clients(api_keys: dict) -> dict:
    """
    Initialiseert LLM clients voor alle geconfigureerde providers.
    
    Returns:
        dict: {model_id: {"client": ..., "provider": ..., "model_name": ...}}
    """
    clients = {}
    
    for model_id, config in api_keys.items():
        provider = config["provider"]
        api_key = config["api_key"]
        
        try:
            if provider == "anthropic":
                clients[model_id] = {
                    "client": Anthropic(api_key=api_key),
                    "provider": "anthropic",
                    "model_name": config["model_name"]
                }
            elif provider == "openai" and OPENAI_BESCHIKBAAR:
                clients[model_id] = {
                    "client": OpenAI(api_key=api_key),
                    "provider": "openai",
                    "model_name": config["model_name"]
                }
            elif provider == "mistral" and MISTRAL_BESCHIKBAAR:
                clients[model_id] = {
                    "client": Mistral(api_key=api_key),
                    "provider": "mistral",
                    "model_name": config["model_name"]
                }
            elif provider == "google" and GOOGLE_BESCHIKBAAR:
                genai.configure(api_key=api_key)
                clients[model_id] = {
                    "client": genai.GenerativeModel(config["model_name"]),
                    "provider": "google",
                    "model_name": config["model_name"]
                }
        except Exception as e:
            st.sidebar.warning(f"⚠️ {model_id}: {e}")
    
    return clients


def maak_vangrail_client(api_keys: dict):
    """
    Maakt een snelle Claude Haiku client voor content moderatie.
    Zoekt naar de eerste Anthropic API key.
    """
    for config in api_keys.values():
        if config["provider"] == "anthropic":
            try:
                return Anthropic(api_key=config["api_key"])
            except Exception:
                pass
    return None
