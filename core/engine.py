"""
Core Engine voor de Leertool Argumenteren
=========================================

Dit is de hoofd logica, onafhankelijk van de UI (Streamlit/React/etc).
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .config import get_actieve_stelling, Stelling
from .agents import Agent, AGENTEN, CV_DATA
from .rag import RAGDatabase, RAGRetriever, create_rag_instruction


@dataclass
class DiscussieResponse:
    """Response van een agent met metadata."""
    tekst: str
    agent_naam: str
    bronnen: List[Dict]
    model_id: str
    model_info: str


class LeertoolEngine:
    """
    Hoofd engine voor de leertool.
    
    Beheert:
    - Stelling configuratie
    - RAG database
    - Agent responses genereren
    - Bronnen tracking
    """
    
    def __init__(self, documents_path: str, llm_clients: dict):
        """
        Initialiseert de engine.
        
        Args:
            documents_path: Pad naar documents folder
            llm_clients: Dict met geïnitialiseerde LLM clients
        """
        self.stelling = get_actieve_stelling()
        self.clients = llm_clients
        self.documents_path = documents_path
        
        # RAG database initialiseren
        self.rag_db = None
        self.rag_retriever = None
        self._init_rag()
    
    def _init_rag(self) -> Dict[str, int]:
        """Initialiseert de RAG database."""
        try:
            self.rag_db = RAGDatabase(self.documents_path)
            stats = self.rag_db.load_documents(self.stelling.id)
            self.rag_retriever = RAGRetriever(self.rag_db)
            return stats
        except Exception as e:
            print(f"RAG initialisatie mislukt: {e}")
            return {}
    
    def get_stelling(self) -> Stelling:
        """Geeft de actieve stelling."""
        return self.stelling
    
    def get_agenten_geshuffeld(self) -> List[str]:
        """Geeft agent namen in willekeurige volgorde."""
        namen = list(AGENTEN.keys())
        random.shuffle(namen)
        return namen
    
    def get_random_model(self) -> Optional[str]:
        """Kiest een random model uit beschikbare clients."""
        if self.clients:
            return random.choice(list(self.clients.keys()))
        return None
    
    def bouw_systeem_prompt(
        self, 
        agent: Agent, 
        gesprek_history: List[Dict],
        rag_context: str = ""
    ) -> str:
        """
        Bouwt de complete systeem prompt voor een agent.
        
        Bevat:
        - Agent basis prompt
        - Stelling context
        - Voorbeeld reacties
        - RAG context (indien beschikbaar)
        - CV details (kans-gebaseerd)
        - Referentie naar eerder gesprek (kans-gebaseerd)
        """
        prompt_delen = []
        
        # 1. Stelling context (ALTIJD)
        prompt_delen.append(f"""=== DISCUSSIE CONTEXT ===
Je neemt deel aan een discussie over de stelling:
"{self.stelling.titel}"

Achtergrondinformatie: {self.stelling.context}
""")
        
        # 2. Agent basis prompt
        prompt_delen.append(f"""=== JOUW ROL ===
{agent.systeem_prompt}
""")
        
        # 3. Voorbeeld reacties (als beschikbaar)
        if agent.voorbeeld_reacties:
            voorbeelden = "\n".join([f"- \"{v}\"" for v in agent.voorbeeld_reacties])
            prompt_delen.append(f"""=== VOORBEELDEN VAN JOUW SPREEKSTIJL ===
{voorbeelden}

Gebruik deze voorbeelden als inspiratie voor je toon en stijl, maar geef unieke antwoorden.
""")
        
        # 4. RAG context (indien beschikbaar)
        if rag_context:
            prompt_delen.append(rag_context)
        
        # 5. CV detail (kans-gebaseerd)
        if agent.naam in CV_DATA and random.random() < agent.p_cv_detail:
            cv = CV_DATA[agent.naam]
            detail_type = random.choice(list(cv.keys()))
            detail = cv[detail_type]
            prompt_delen.append(f"""
=== PERSOONLIJK DETAIL ===
VERWERK DIT SUBTIEL IN JE ANTWOORD: {detail}
""")
        
        # 6. Referentie naar eerder gesprek (kans-gebaseerd)
        if gesprek_history and random.random() < agent.p_referentie:
            # Zoek een eerdere user message om naar te verwijzen
            user_msgs = [m for m in gesprek_history if m.get("role") == "user"]
            if user_msgs:
                eerdere_msg = random.choice(user_msgs)["content"][:50]
                prompt_delen.append(f"""
=== GESPREKSREFERENTIE ===
VERWIJS KORT NAAR IETS DAT EERDER IS GEZEGD (bijv. over "{eerdere_msg}...")
""")
        
        return "\n".join(prompt_delen)
    
    def genereer_response(
        self,
        agent_naam: str,
        user_bericht: str,
        gesprek_history: List[Dict],
        model_id: str
    ) -> DiscussieResponse:
        """
        Genereert een response van een agent.
        
        Args:
            agent_naam: Naam van de agent
            user_bericht: Het bericht van de gebruiker
            gesprek_history: Eerdere berichten in het gesprek
            model_id: ID van het te gebruiken model
            
        Returns:
            DiscussieResponse met tekst, bronnen en metadata
        """
        agent = AGENTEN[agent_naam]
        bronnen = []
        rag_context = ""
        
        # RAG context ophalen (indien beschikbaar en agent gebruikt bronnen)
        if self.rag_retriever and agent.standpunt != "GEEN":
            if random.random() < agent.p_bronnen:
                context, bronnen = self.rag_retriever.get_context_for_agent(
                    user_bericht,
                    agent.standpunt,
                    n_results=2
                )
                if context:
                    rag_context = create_rag_instruction(context, bronnen)
        
        # Systeem prompt bouwen
        systeem_prompt = self.bouw_systeem_prompt(agent, gesprek_history, rag_context)
        
        # Messages voorbereiden
        messages = []
        for msg in gesprek_history:
            if msg.get("role") in ["user", "assistant"]:
                content = msg.get("content", "")
                # Strip agent naam uit assistant berichten
                if ":\n\n" in content:
                    content = content.split(":\n\n", 1)[-1]
                messages.append({"role": msg["role"], "content": content})
        messages.append({"role": "user", "content": user_bericht})
        
        # Response genereren via LLM
        client_info = self.clients.get(model_id, {})
        response_tekst = self._call_llm(client_info, systeem_prompt, messages, agent.max_tokens)
        
        return DiscussieResponse(
            tekst=response_tekst,
            agent_naam=agent_naam,
            bronnen=bronnen,
            model_id=model_id,
            model_info=f"{client_info.get('provider', '?')}/{client_info.get('model_name', '?')}"
        )
    
    def _call_llm(
        self, 
        client_info: dict, 
        systeem_prompt: str, 
        messages: List[Dict],
        max_tokens: int
    ) -> str:
        """Roept de LLM aan en retourneert de response tekst."""
        if not client_info:
            return "[Model niet beschikbaar]"
        
        provider = client_info.get("provider")
        client = client_info.get("client")
        model_name = client_info.get("model_name")
        
        try:
            if provider == "anthropic":
                response = client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    system=systeem_prompt,
                    messages=messages
                )
                return response.content[0].text
                
            elif provider == "openai":
                openai_msgs = [{"role": "system", "content": systeem_prompt}] + messages
                response = client.chat.completions.create(
                    model=model_name,
                    max_completion_tokens=max_tokens,
                    messages=openai_msgs
                )
                return response.choices[0].message.content
                
            elif provider == "mistral":
                mistral_msgs = [{"role": "system", "content": systeem_prompt}] + messages
                response = client.chat.complete(
                    model=model_name,
                    max_tokens=max_tokens,
                    messages=mistral_msgs
                )
                return response.choices[0].message.content
                
            elif provider == "google":
                conv = f"Instructie: {systeem_prompt}\n\n"
                for msg in messages:
                    role = "Gebruiker" if msg["role"] == "user" else "Assistent"
                    conv += f"{role}: {msg['content']}\n"
                response = client.generate_content(conv)
                return response.text
            
            else:
                return "[Onbekende provider]"
                
        except Exception as e:
            return f"[Fout: {e}]"
    
    def zoek_bron(self, tekst: str) -> Optional[Dict]:
        """
        Zoekt de bron van een stuk tekst.
        
        Args:
            tekst: De tekst om te zoeken
            
        Returns:
            Bron info of None
        """
        if self.rag_retriever:
            return self.rag_db.find_source(tekst)
        return None
    
    def genereer_uitleg(
        self,
        tekst: str,
        niveau: str,
        model_id: str
    ) -> str:
        """
        Genereert uitleg van tekst op een bepaald niveau.
        
        Args:
            tekst: De tekst om uit te leggen
            niveau: "groep_6", "groep_7", of "groep_8"
            model_id: ID van het te gebruiken model
            
        Returns:
            Uitleg tekst
        """
        from .utils.discussiemeester import maak_uitleg_prompt
        
        prompt = maak_uitleg_prompt(tekst, niveau)
        client_info = self.clients.get(model_id, {})
        
        return self._call_llm(
            client_info,
            "Je bent een vriendelijke leraar.",
            [{"role": "user", "content": prompt}],
            max_tokens=300
        )
