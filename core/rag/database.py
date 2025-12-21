"""
RAG Database Module
===================

Beheert de ChromaDB vector database voor het opslaan en ophalen
van documenten (artikelen, social media posts, etc.)
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import hashlib


class RAGDatabase:
    """
    Vector database voor PRO, CONTRA en FAKENEWS documenten.
    Gebruikt ChromaDB met sentence-transformers voor embeddings.
    """
    
    def __init__(self, documents_path: str):
        """
        Initialiseert de database.
        
        Args:
            documents_path: Pad naar de documents folder
        """
        self.documents_path = documents_path
        
        # ChromaDB client (in-memory voor Streamlit Cloud)
        self.client = chromadb.Client()
        
        # Embedding functie (gratis, lokaal)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Collecties voor elk standpunt
        self.collections = {}
    
    def _parse_document(self, filepath: str) -> Dict:
        """
        Leest een document en extraheert metadata en content.
        
        Verwacht formaat:
        ---
        bron: Twitter
        auteur: @GroenLinks
        datum: 2024-03-15
        url: https://...
        type: social_media
        ---
        
        De eigenlijke content hier...
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "bron": "Onbekend",
            "auteur": "Onbekend",
            "datum": "",
            "url": "",
            "type": "artikel"
        }
        
        text = content
        
        # Parse metadata als aanwezig
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                meta_lines = parts[1].strip().split('\n')
                for line in meta_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip().lower()] = value.strip()
                text = parts[2].strip()
        
        return {"metadata": metadata, "content": text}
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Splitst tekst in chunks. Korte teksten blijven intact."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            
            if end < len(text):
                last_period = text.rfind('.', start, end)
                last_question = text.rfind('?', start, end)
                last_exclaim = text.rfind('!', start, end)
                best_break = max(last_period, last_question, last_exclaim)
                
                if best_break > start + chunk_size // 2:
                    end = best_break + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    def _generate_id(self, text: str, metadata: Dict) -> str:
        """Genereert een unieke ID voor een chunk."""
        unique_str = f"{metadata['filepath']}_{text[:50]}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def load_documents(self, stelling: str = "elektrische_autos") -> Dict[str, int]:
        """
        Laadt alle documenten voor een stelling.
        
        Returns:
            Dict met aantal geladen documenten per standpunt
        """
        stats = {"PRO": 0, "CONTRA": 0, "FAKENEWS": 0}
        
        for standpunt in ["PRO", "CONTRA", "FAKENEWS"]:
            collection_name = f"{stelling}_{standpunt}".lower().replace(" ", "_")
            
            try:
                self.client.delete_collection(collection_name)
            except:
                pass
            
            self.collections[standpunt] = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )
            
            standpunt_path = os.path.join(self.documents_path, stelling, standpunt)
            
            if not os.path.exists(standpunt_path):
                continue
            
            documents = []
            metadatas = []
            ids = []
            
            for root, dirs, files in os.walk(standpunt_path):
                for filename in files:
                    if filename.endswith(('.txt', '.md')):
                        filepath = os.path.join(root, filename)
                        
                        try:
                            doc = self._parse_document(filepath)
                            chunks = self._chunk_text(doc["content"])
                            
                            for i, chunk in enumerate(chunks):
                                chunk_metadata = doc["metadata"].copy()
                                chunk_metadata["chunk_index"] = i
                                chunk_metadata["total_chunks"] = len(chunks)
                                chunk_metadata["standpunt"] = standpunt
                                
                                documents.append(chunk)
                                metadatas.append(chunk_metadata)
                                ids.append(self._generate_id(chunk, chunk_metadata))
                            
                            stats[standpunt] += 1
                        except Exception as e:
                            print(f"Fout bij laden {filepath}: {e}")
            
            if documents:
                self.collections[standpunt].add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
        
        return stats
    
    def search(self, query: str, standpunt: str, n_results: int = 3) -> List[Dict]:
        """Zoekt relevante documenten."""
        if standpunt not in self.collections:
            return []
        
        results = self.collections[standpunt].query(
            query_texts=[query],
            n_results=n_results
        )
        
        formatted = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted
    
    def find_source(self, text: str) -> Optional[Dict]:
        """Zoekt de bron van een stuk tekst."""
        best_match = None
        best_distance = float('inf')
        
        for standpunt in ["PRO", "CONTRA", "FAKENEWS"]:
            if standpunt not in self.collections:
                continue
            
            results = self.collections[standpunt].query(
                query_texts=[text],
                n_results=1
            )
            
            if results and results['distances'] and results['distances'][0]:
                distance = results['distances'][0][0]
                if distance < best_distance:
                    best_distance = distance
                    best_match = {
                        "content": results['documents'][0][0],
                        "metadata": results['metadatas'][0][0],
                        "distance": distance,
                        "standpunt": standpunt
                    }
        
        return best_match
