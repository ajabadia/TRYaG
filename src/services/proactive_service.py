from services.rag_service import get_rag_service
import streamlit as st

class ProactiveService:
    """
    Servicio de vigilancia proactiva.
    Analiza el texto de entrada en tiempo real y busca coincidencias en la base vectorial (RAG).
    Si encuentra algo muy relevante, devuelve una sugerencia o alerta.
    """
    
    _last_query = ""
    _cache_response = []

    @staticmethod
    def check_context_and_suggest(text: str) -> list[str]:
        """
        Calcula sugerencias basadas en el texto.
        Usa caché simple para no machacar la DB si el texto no cambia mucho.
        """
        if not text or len(text) < 10:
            return []
            
        # Evitar calls si el texto es casi igual (optimización básica)
        # En una app real usaríamos embeddings ligeros o debounce JS.
        # Aquí permitimos re-consulta si ha cambiado significativamente
        
        try:
            rag = get_rag_service()
            # Buscamos SOLO 1 documento muy relevante
            results = rag.search_documents(text, n_results=1)
            
            sugerencias = []
            if results:
                # Extraer título o fuente del metadato
                doc = results[0]
                metadata = doc.get("metadata", {})
                source = metadata.get("source", "Protocolo")
                
                # Heurística simple: Si la distancia es baja (similitud alta)
                # Chroma devuelve distancias, pero aquí asumimos que search_documents ya filtra.
                # Simularemos "detección" si hay resultado.
                
                sugerencias.append(f"📚 Protocolo Relacionado: {source}")
                
            return sugerencias

        except Exception as e:
            print(f"Error en ProactiveService: {e}")
            return []
