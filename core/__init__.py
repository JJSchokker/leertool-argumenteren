"""
Core Module - Leertool Argumenteren

Onafhankelijk van UI (Streamlit/React/etc).
"""

from .config import (
    Stelling,
    STELLINGEN,
    get_actieve_stelling,
    get_stelling_by_id,
    get_alle_stellingen,
    ACTIEVE_STELLING_ID
)
from .engine import LeertoolEngine, DiscussieResponse
from .agents import Agent, AGENTEN, get_agent, get_alle_agenten, CV_DATA
from .llm import laad_api_keys, initialiseer_clients, maak_vangrail_client, check_veiligheid
from .rag import RAGDatabase, RAGRetriever, create_rag_instruction
from .utils import log_response, lees_log, maak_uitleg_prompt, format_bron_resultaat, NIVEAU_LABELS

__all__ = [
    # Config
    'Stelling', 'STELLINGEN', 'get_actieve_stelling', 
    'get_stelling_by_id', 'get_alle_stellingen', 'ACTIEVE_STELLING_ID',
    
    # Engine
    'LeertoolEngine', 'DiscussieResponse',
    
    # Agents
    'Agent', 'AGENTEN', 'get_agent', 'get_alle_agenten', 'CV_DATA',
    
    # LLM
    'laad_api_keys', 'initialiseer_clients', 'maak_vangrail_client', 'check_veiligheid',
    
    # RAG
    'RAGDatabase', 'RAGRetriever', 'create_rag_instruction',
    
    # Utils
    'log_response', 'lees_log', 'maak_uitleg_prompt', 'format_bron_resultaat', 'NIVEAU_LABELS',
]
