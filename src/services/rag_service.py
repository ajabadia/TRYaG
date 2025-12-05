import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
import streamlit as st

# Configuración de persistencia
CHROMA_DB_DIR = os.path.join(os.getcwd(), "data", "chroma_db")
COLLECTION_NAME = "triage_knowledge_base"

class RAGService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa el cliente de ChromaDB y la colección."""
        if not os.path.exists(CHROMA_DB_DIR):
            os.makedirs(CHROMA_DB_DIR)
            
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        
        # Usamos el modelo de embedding por defecto de Chroma (all-MiniLM-L6-v2)
        # Es ligero y corre en local CPU.
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        
    def ingest_document(self, file_obj, filename: str) -> bool:
        """
        Procesa un archivo (PDF/TXT/MD), lo guarda en disco, lo divide en chunks y lo indexa.
        """
        try:
            # 1. Guardar archivo físico en data/rag_docs
            docs_dir = os.path.join(os.getcwd(), "data", "rag_docs")
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
                
            file_path = os.path.join(docs_dir, filename)
            
            # Guardar el contenido
            # file_obj viene de st.file_uploader, es un BytesIO-like
            file_content = file_obj.getvalue()
            with open(file_path, "wb") as f:
                f.write(file_content)
                
            # 2. Procesar texto
            text = ""
            if filename.lower().endswith(".pdf"):
                # Usar el archivo guardado o el objeto en memoria
                pdf_reader = pypdf.PdfReader(file_obj)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            else:
                # Asumimos texto plano o markdown
                text = file_content.decode("utf-8")
                
            if not text.strip():
                return False
                
            # Dividir en chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunks = text_splitter.split_text(text)
            
            # Preparar datos para Chroma
            ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
            
            # Insertar (upsert)
            self.collection.upsert(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            return True
            
        except Exception as e:
            print(f"Error ingesting document {filename}: {e}")
            return False

    def search_context(self, query: str, n_results: int = 3) -> List[str]:
        """
        Busca los fragmentos más relevantes para una query.
        Retorna solo texto (para compatibilidad con triage_service).
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results and results['documents']:
                return results['documents'][0]
            return []
            
        except Exception as e:
            print(f"Error searching context: {e}")
            return []

    def search_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Busca fragmentos y devuelve texto + metadatos.
        Ideal para el buscador UI.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas']
            )
            
            output = []
            if results and results['documents']:
                docs = results['documents'][0]
                metas = results['metadatas'][0]
                
                for i in range(len(docs)):
                    output.append({
                        "content": docs[i],
                        "metadata": metas[i]
                    })
            return output
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def get_indexed_documents(self) -> List[Dict]:
        """
        Devuelve una lista de documentos únicos indexados.
        Nota: Chroma no tiene una API directa para esto, así que iteramos metadatos.
        Esto puede ser lento si hay muchos datos, idealmente mantendríamos un registro aparte.
        """
        try:
            # Hack: obtener todos los metadatos (limitado a 10000 por defecto)
            # Para producción, mejor mantener una tabla SQL/Mongo de archivos indexados.
            result = self.collection.get(include=['metadatas'])
            if not result or not result['metadatas']:
                return []
                
            files = {}
            for meta in result['metadatas']:
                source = meta.get('source')
                if source:
                    if source not in files:
                        files[source] = 0
                    files[source] += 1
            
            return [{"filename": k, "chunks": v} for k, v in files.items()]
            
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def delete_document(self, filename: str) -> bool:
        """
        Elimina todos los chunks asociados a un archivo y el archivo físico.
        """
        try:
            # 1. Eliminar de ChromaDB
            self.collection.delete(
                where={"source": filename}
            )
            
            # 2. Eliminar archivo físico
            file_path = os.path.join(os.getcwd(), "data", "rag_docs", filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return True
        except Exception as e:
            print(f"Error deleting document {filename}: {e}")
            return False

    def get_document_path(self, filename: str) -> Optional[str]:
        """Devuelve la ruta absoluta del archivo si existe."""
        file_path = os.path.join(os.getcwd(), "data", "rag_docs", filename)
        if os.path.exists(file_path):
            return file_path
        return None

# Singleton helper
def get_rag_service():
    return RAGService()
