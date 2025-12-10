"""
Leertool Argumenteren
==============================

Een educatieve tool voor basisschoolleerlingen (bovenbouw groep 6/7/8) om kritisch 
denken en mediawijsheid te oefenen via gesimuleerde online discussies.

"""

import streamlit as st
import os
from datetime import datetime

# Lokale modules
from agents import AGENTEN
from llm import (
    laad_api_keys,
    initialiseer_clients,
    maak_vangrail_client,
    genereer_response,
    vraag_uitleg,
    check_veiligheid,
)
from utils import context_weaver, log_response, lees_log

# =============================================================================
# CONFIGURATIE
# =============================================================================

st.set_page_config(
    page_title="Leertool Argumenteren",
    page_icon="",
    layout="wide"
)

# API keys en clients laden
API_KEYS = laad_api_keys()
clients = initialiseer_clients(API_KEYS)
vangrail_client = maak_vangrail_client(API_KEYS)

# Pad naar assets
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

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
        background-color: #ffebee; 
        border-left: 5px solid #d32f2f; 
        padding: 15px; 
        border-radius: 5px; 
        color: #b71c1c; 
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
    st.title("Leertool Argumenteren")
     st.markdown(
        '<div class="stelling-box">De stelling van vandaag: '
        '<em>"Elektrisch rijden is goed voor het milieu"</em></div>',
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
    st.session_state.selected_model = None
if "start_tijd" not in st.session_state:
    st.session_state.start_tijd = None
if "tijd_is_om" not in st.session_state:
    st.session_state.tijd_is_om = False
if "aantekeningen" not in st.session_state:
    st.session_state.aantekeningen = ""

# =============================================================================
# LAYOUT
# =============================================================================

col1, col2 = st.columns([1, 2])

# --- LINKER KOLOM: Controls ---
with col1:
    
    # Model selectie
    st.subheader("Kies Model")
    model_cols = st.columns(4)
    for i, col in enumerate(model_cols):
        model_id = f"model_{i+1}"
        with col:
            btn_type = "primary" if st.session_state.selected_model == model_id else "secondary"
            if st.button(f"M{i+1}", use_container_width=True, type=btn_type):
                st.session_state.selected_model = model_id
                st.session_state.messages = []
                st.rerun()
    
    if st.session_state.selected_model:
        st.success(f"✓ {st.session_state.selected_model.replace('_', ' ').title()}")
    
    st.divider()
    
    # Timer
    st.subheader("Tijd")
    TIJD_MINUTEN = 15
    
    if st.session_state.start_tijd is None:
        if st.button("Start Discussie", type="primary", use_container_width=True):
            st.session_state.start_tijd = datetime.now()
            st.session_state.messages = []
            st.session_state.tijd_is_om = False
            st.rerun()
    else:
        verstreken = (datetime.now() - st.session_state.start_tijd).total_seconds()
        progressie = min(verstreken / (TIJD_MINUTEN * 60), 1.0)
        st.progress(progressie)
        
        if progressie >= 1.0:
            st.session_state.tijd_is_om = True
            st.error("🏁 Tijd is om!")
        else:
            rest = (TIJD_MINUTEN * 60) - verstreken
            st.caption(f"⏰ {int(rest//60)}:{int(rest%60):02d}")
    
    st.divider()
    
    # Agent selectie
    st.subheader("👥 Gesprekspartners")
    agent_naam = st.selectbox(
        "Kies wie je wilt spreken:",
        list(AGENTEN.keys()),
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
    
    # Hulp functie
    with st.expander("Vraag om uitleg"):
        uitleg_tekst = st.text_area(
            "Plak tekst om uitleg te krijgen:",
            height=60,
            key="uitleg",
            label_visibility="collapsed"
        )
        if st.button("Leg uit"):
            if uitleg_tekst and st.session_state.selected_model:
                uitleg = vraag_uitleg(clients, st.session_state.selected_model, uitleg_tekst)
                st.markdown(
                    f"<div class='discussieleider-box'>👩‍🏫 {uitleg}</div>",
                    unsafe_allow_html=True
                )
    
    st.divider()
    
    # Notities
    st.subheader("Schrijf hier je argumenten")
    st.session_state.aantekeningen = st.text_area(
        "Maak aantekeningen:",
        st.session_state.aantekeningen,
        height=120,
        label_visibility="collapsed"
    )
    if st.session_state.aantekeningen:
        st.download_button(
            "Download",
            st.session_state.aantekeningen,
            "notities.txt"
        )

# --- RECHTER KOLOM: Chat ---
with col2:
    st.subheader("Discussie")
    
    # Chat container
    chat_container = st.container(height=480)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg.get("is_html"):
                    st.markdown(msg["content"], unsafe_allow_html=True)
                else:
                    st.write(msg["content"])
    
    # Status checks en chat input
    if not st.session_state.selected_model:
        st.warning("👈 Selecteer eerst een model")
    elif st.session_state.start_tijd is None:
        st.info("👈 Klik op 'Start Discussie' om te beginnen")
    elif st.session_state.tijd_is_om:
        st.warning("⏰ De tijd is voorbij!")
        if st.button("🔄 Opnieuw beginnen"):
            st.session_state.start_tijd = None
            st.session_state.messages = []
            st.session_state.tijd_is_om = False
            st.rerun()
    elif not agent_naam:
        st.info("👆 Kies een gesprekspartner")
    else:
        # Chat input
        if prompt := st.chat_input(f"Zeg iets tegen {agent_naam}..."):
            # User bericht toevoegen
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Veiligheidscheck (vangrail)
            if check_veiligheid(vangrail_client, prompt):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "<div class='discussieleider-box'>👩‍🏫 Let op je taalgebruik!</div>",
                    "is_html": True
                })
            else:
                # Response genereren
                agent = AGENTEN[agent_naam]
                
                # Messages voorbereiden
                messages = []
                for msg in st.session_state.messages[:-1]:
                    if msg["role"] in ["user", "assistant"] and not msg.get("is_html"):
                        content = msg["content"]
                        if ":\n\n" in content:
                            content = content.split(":\n\n", 1)[-1]
                        messages.append({"role": msg["role"], "content": content})
                messages.append({"role": "user", "content": prompt})
                
                # Context en response
                systeem_prompt = context_weaver(agent, st.session_state.messages[:-1])
                
                with st.spinner(f"{agent.naam} denkt na..."):
                    response = genereer_response(
                        clients,
                        st.session_state.selected_model,
                        systeem_prompt,
                        messages
                    )
                
                # Loggen
                log_response(
                    API_KEYS,
                    st.session_state.selected_model,
                    agent.naam,
                    prompt,
                    response
                )
                
                # Response toevoegen
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**{agent.naam}**:\n\n{response}",
                    "is_html": False
                })
            
            st.rerun()

# =============================================================================
# FOOTER
# =============================================================================

st.divider()

col_f1, col_f2 = st.columns([2, 1])

with col_f1:
    st.caption("Leertool Argumenteren | Model Vergelijking")

with col_f2:
    log_content = lees_log()
    if log_content:
        st.download_button(
            "📥 Download Log",
            log_content,
            "model_responses_log.json",
            "application/json"
        )
    else:
        st.caption("Nog geen log beschikbaar")
