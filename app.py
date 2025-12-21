"""
Leertool Argumenteren - Streamlit App
=====================================

Entry point voor Streamlit Cloud deployment.
"""

import streamlit as st
import os
import sys

# Core modules importeren
from core import (
    LeertoolEngine,
    get_actieve_stelling,
    AGENTEN,
    laad_api_keys,
    initialiseer_clients,
    maak_vangrail_client,
    check_veiligheid,
    log_response,
    lees_log,
    format_bron_resultaat,
    NIVEAU_LABELS,
)

# =============================================================================
# CONFIGURATIE
# =============================================================================

st.set_page_config(
    page_title="Socrates Leertool Argumenteren",
    page_icon="🏛️",
    layout="wide"
)

# Paden
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
DOCUMENTS_DIR = os.path.join(SCRIPT_DIR, "documents")

# API en clients
API_KEYS = laad_api_keys()
clients = initialiseer_clients(API_KEYS)
vangrail_client = maak_vangrail_client(API_KEYS)

# Engine initialiseren (cached)
@st.cache_resource
def get_engine():
    return LeertoolEngine(DOCUMENTS_DIR, clients)

try:
    engine = get_engine()
    ENGINE_OK = True
except Exception as e:
    ENGINE_OK = False
    st.error(f"Engine kon niet starten: {e}")

stelling = get_actieve_stelling()

# =============================================================================
# STYLING
# =============================================================================

st.markdown("""
<style>
    .stelling-box { 
        background-color: #e3f2fd; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: bold; 
        margin-bottom: 20px; 
    }
    .discussieleider-box { 
        background-color: #fff3e0; 
        border-left: 5px solid #ff9800; 
        padding: 15px; 
        border-radius: 5px; 
    }
    .waarschuwing-box { 
        background-color: #ffebee; 
        border-left: 5px solid #d32f2f; 
        padding: 15px; 
        border-radius: 5px; 
        color: #b71c1c; 
    }
    .bron-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 15px;
        border-radius: 5px;
    }
    .fakenews-box {
        background-color: #fce4ec;
        border-left: 5px solid #e91e63;
        padding: 15px;
        border-radius: 5px;
    }
    .agent-profiel { 
        background-color: #f5f5f5; 
        padding: 10px; 
        border-radius: 8px; 
        font-size: 0.9em; 
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================

header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title("Socrates Leertool Argumenteren")
    st.markdown(
        f'<div class="stelling-box">De stelling van vandaag: '
        f'<em>"{stelling.titel}"</em></div>',
        unsafe_allow_html=True
    )

with header_col2:
    header_img = os.path.join(ASSETS_DIR, "socrates_header.jpeg")
    if os.path.exists(header_img):
        st.image(header_img, width=200)

# =============================================================================
# SESSION STATE
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = engine.get_random_model() if ENGINE_OK else None
if "agent_volgorde" not in st.session_state:
    st.session_state.agent_volgorde = engine.get_agenten_geshuffeld() if ENGINE_OK else list(AGENTEN.keys())
if "discussie_actief" not in st.session_state:
    st.session_state.discussie_actief = False
if "aantekeningen" not in st.session_state:
    st.session_state.aantekeningen = ""

# =============================================================================
# LAYOUT
# =============================================================================

col1, col2 = st.columns([1, 2])

# --- LINKER KOLOM ---
with col1:
    
    # Start knop
    if not st.session_state.discussie_actief:
        if st.button("🚀 Start Discussie", type="primary", use_container_width=True):
            st.session_state.discussie_actief = True
            st.session_state.messages = []
            st.rerun()
    else:
        st.success("✅ Discussie actief")
        if st.button("🔄 Opnieuw beginnen"):
            st.session_state.discussie_actief = False
            st.session_state.messages = []
            if ENGINE_OK:
                st.session_state.selected_model = engine.get_random_model()
                st.session_state.agent_volgorde = engine.get_agenten_geshuffeld()
            st.rerun()
    
    st.divider()
    
    # Agent selectie
    st.subheader("👥 Gesprekspartner")
    agent_naam = st.selectbox(
        "Kies wie je wilt spreken:",
        st.session_state.agent_volgorde,
        index=None,
        placeholder="Selecteer...",
        label_visibility="collapsed"
    )
    
    if agent_naam:
        agent = AGENTEN[agent_naam]
        avatar_path = os.path.join(ASSETS_DIR, "avatars", agent.avatar_bestand)
        if os.path.exists(avatar_path):
            st.image(avatar_path, width=100)
        st.markdown(f"**{agent.naam}**")
        st.markdown(
            f"<div class='agent-profiel'>{agent.publiek_profiel}</div>",
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # Discussiemeester
    st.subheader("👩‍🏫 Discussiemeester")
    
    dm_tekst = st.text_area(
        "Plak tekst uit de chat:",
        height=80,
        placeholder="Kopieer en plak hier tekst...",
        label_visibility="collapsed",
        key="dm_tekst"
    )
    
    dm_niveau = st.radio(
        "Niveau:",
        options=["groep_6", "groep_7", "groep_8"],
        format_func=lambda x: NIVEAU_LABELS[x],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    dm_col1, dm_col2 = st.columns(2)
    
    with dm_col1:
        if st.button("📖 Uitleg", use_container_width=True):
            if dm_tekst and st.session_state.selected_model and ENGINE_OK:
                with st.spinner("Uitleg maken..."):
                    uitleg = engine.genereer_uitleg(
                        dm_tekst, 
                        dm_niveau, 
                        st.session_state.selected_model
                    )
                    st.markdown(
                        f"<div class='discussieleider-box'>📖 <strong>Uitleg ({NIVEAU_LABELS[dm_niveau]}):</strong><br>{uitleg}</div>",
                        unsafe_allow_html=True
                    )
    
    with dm_col2:
        if st.button("📚 Bronnen", use_container_width=True):
            if dm_tekst and ENGINE_OK:
                with st.spinner("Bronnen zoeken..."):
                    bron = engine.zoek_bron(dm_tekst)
                    if bron:
                        if bron.get("standpunt") == "FAKENEWS":
                            st.markdown(
                                "<div class='fakenews-box'>⚠️ <strong>Let op! Dit lijkt op nepnieuws of onbetrouwbare informatie!</strong></div>",
                                unsafe_allow_html=True
                            )
                        else:
                            bron_info = engine.rag_retriever.format_source_for_user(bron)
                            st.markdown(
                                f"<div class='bron-box'>{format_bron_resultaat(bron_info, dm_tekst)}</div>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.markdown(
                            f"<div class='discussieleider-box'>{format_bron_resultaat(None, dm_tekst)}</div>",
                            unsafe_allow_html=True
                        )
    
    st.divider()
    
    # Notities
    st.subheader("📝 Notities")
    st.session_state.aantekeningen = st.text_area(
        "Maak aantekeningen:",
        st.session_state.aantekeningen,
        height=100,
        label_visibility="collapsed"
    )
    
    if st.session_state.aantekeningen:
        st.download_button(
            "💾 Download notities",
            st.session_state.aantekeningen,
            "notities.txt"
        )

# --- RECHTER KOLOM: Chat ---
with col2:
    st.subheader("💬 Discussie")
    
    # Chat container
    chat_container = st.container(height=480)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg.get("is_html"):
                    st.markdown(msg["content"], unsafe_allow_html=True)
                else:
                    st.write(msg["content"])
    
    # Status en input
    if not ENGINE_OK:
        st.error("⚠️ Engine niet beschikbaar")
    elif not st.session_state.selected_model:
        st.error("⚠️ Geen model beschikbaar")
    elif not st.session_state.discussie_actief:
        st.info("👈 Klik op 'Start Discussie' om te beginnen")
    elif not agent_naam:
        st.info("👆 Kies een gesprekspartner")
    else:
        if prompt := st.chat_input(f"Zeg iets tegen {agent_naam}..."):
            # User bericht toevoegen
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Veiligheidscheck
            if check_veiligheid(vangrail_client, prompt):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "<div class='waarschuwing-box'>👩‍🏫 Let op je taalgebruik!</div>",
                    "is_html": True
                })
            else:
                # Response genereren via engine
                with st.spinner(f"{agent_naam} denkt na..."):
                    response = engine.genereer_response(
                        agent_naam,
                        prompt,
                        st.session_state.messages[:-1],
                        st.session_state.selected_model
                    )
                
                # Loggen
                log_response(
                    model_id=response.model_id,
                    model_info=response.model_info,
                    agent_naam=response.agent_naam,
                    vraag=prompt,
                    antwoord=response.tekst,
                    stelling=stelling.titel,
                    bronnen=response.bronnen
                )
                
                # Response toevoegen
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**{response.agent_naam}**:\n\n{response.tekst}",
                    "is_html": False
                })
            
            st.rerun()

# =============================================================================
# FOOTER
# =============================================================================

st.divider()

col_f1, col_f2 = st.columns([2, 1])

with col_f1:
    st.caption(f"Socrates Leertool Argumenteren | Stelling: {stelling.id}")

with col_f2:
    log_content = lees_log()
    if log_content:
        st.download_button(
            "📥 Download Log",
            log_content,
            "model_responses_log.json",
            "application/json"
        )
