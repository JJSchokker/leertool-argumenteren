"""
RAG Retriever Module
====================

Haalt relevante context op uit de database.
"""

from typing import List, Dict, Optional, Tuple
from .database import RAGDatabase


class RAGRetriever:
    """Retriever voor het ophalen van relevante bronnen."""
    
    def __init__(self, database: RAGDatabase):
        self.db = database
    
    def get_context_for_agent(
        self, 
        query: str, 
        standpunt: str, 
        n_results: int = 2
    ) -> Tuple[str, List[Dict]]:
        """
        Haalt relevante context op voor een agent.
        
        Returns:
            Tuple van (context string, lijst met bronnen)
        """
        if standpunt == "GEEN":
            return "", []
        
        results = self.db.search(query, standpunt, n_results)
        
        if not results:
            return "", []
        
        context_parts = []
        bronnen = []
        
        for i, result in enumerate(results):
            meta = result["metadata"]
            content = result["content"]
            
            bron_ref = f"[Bron {i+1}]"
            if meta.get("auteur") and meta["auteur"] != "Onbekend":
                bron_ref = f"[{meta['auteur']}]"
            elif meta.get("bron") and meta["bron"] != "Onbekend":
                bron_ref = f"[{meta['bron']}]"
            
            context_parts.append(f"{bron_ref}: {content}")
            
            bronnen.append({
                "bron_id": f"bron_{i+1}",
                "document": meta.get("filename", "Onbekend"),
                "bron": meta.get("bron", "Onbekend"),
                "auteur": meta.get("auteur", "Onbekend"),
                "datum": meta.get("datum", ""),
                "url": meta.get("url", ""),
                "type": meta.get("type", "artikel"),
                "chunk": content[:200] + "..." if len(content) > 200 else content,
                "relevantie_score": 1 - result.get("distance", 0)
            })
        
        return "\n\n".join(context_parts), bronnen
    
    def format_source_for_user(self, source: Dict) -> str:
        """Formatteert een bron voor weergave."""
        meta = source.get("metadata", source)
        
        lines = []
        
        source_type = meta.get("type", "artikel")
        if source_type == "social_media":
            lines.append("📱 **Social Media Post**")
        elif source_type in ["complot", "onzin"]:
            lines.append("⚠️ **Onbetrouwbare bron**")
        else:
            lines.append("📄 **Artikel**")
        
        auteur = meta.get("auteur", "Onbekend")
        if auteur != "Onbekend":
            lines.append(f"✍️ Auteur: {auteur}")
        
        bron = meta.get("bron", "Onbekend")
        if bron != "Onbekend":
            lines.append(f"📰 Bron: {bron}")
        
        datum = meta.get("datum", "")
        if datum:
            lines.append(f"📅 Datum: {datum}")
        
        standpunt = source.get("standpunt", meta.get("standpunt", ""))
        if standpunt:
            if standpunt == "PRO":
                lines.append("👍 Standpunt: VOOR")
            elif standpunt == "CONTRA":
                lines.append("👎 Standpunt: TEGEN")
            elif standpunt == "FAKENEWS":
                lines.append("🚨 Let op: mogelijk onbetrouwbaar!")
        
        return "\n".join(lines)
    
    def find_source_for_text(self, text: str) -> Optional[str]:
        """Zoekt de bron van tekst en formatteert het resultaat."""
        source = self.db.find_source(text)
        
        if not source or source.get("distance", 1) > 0.5:
            return None
        
        return self.format_source_for_user(source)


def create_rag_instruction(context: str, bronnen: List[Dict]) -> str:
    """Maakt een instructie voor de LLM om RAG context te gebruiken."""
    if not context:
        return ""
    
    return f"""
=== GEBRUIK DEZE INFORMATIE ===

{context}

INSTRUCTIES:
- Baseer je antwoord op bovenstaande informatie
- Zeg het in je eigen woorden
- Noem de bron als dat natuurlijk voelt
- Verzin geen feiten die niet in de bronnen staan
"""
