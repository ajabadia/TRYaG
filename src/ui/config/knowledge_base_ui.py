import streamlit as st
from services.rag_service import get_rag_service
import pandas as pd

def render_knowledge_base_ui():
    """
    Renderiza la interfaz de gestión de la Base de Conocimiento (RAG).
    """
    rag_service = get_rag_service()

    st.markdown("### 📚 Base de Conocimiento (RAG)")
    st.markdown("Gestiona los documentos que la IA utiliza como referencia para sus decisiones.")
    
    # --- BUSCADOR DE PROTOCOLOS ---
    st.markdown("#### 🔍 Buscador de Protocolos")
    st.info("El buscador ahora está disponible como una herramienta global en la barra lateral.")
    
    from components.knowledge_base.protocol_search import show_protocol_search_modal
    if st.button("Abrir Buscador de Protocolos", icon="🔍", use_container_width=True):
        show_protocol_search_modal()
            
    st.divider()

    # --- CARGA DE DOCUMENTOS ---
    with st.expander("📤 Subir Nuevo Documento", expanded=True):
        uploaded_file = st.file_uploader(
            "Selecciona un archivo", 
            type=["pdf", "txt", "md"],
            help="Sube protocolos, guías clínicas o normativa interna."
        )
        
        if uploaded_file:
            if st.button("Procesar e Indexar", type="primary"):
                with st.spinner("Procesando documento... Esto puede tardar unos segundos."):
                    success = rag_service.ingest_document(uploaded_file, uploaded_file.name)
                    if success:
                        st.success(f"✅ {uploaded_file.name} indexado correctamente.")
                        st.rerun()
                    else:
                        st.error("❌ Error al procesar el documento.")

    st.divider()
    
    # Lista de Documentos
    st.markdown("#### 📑 Documentos Indexados")
    
    docs = rag_service.get_indexed_documents()
    
    if not docs:
        st.info("No hay documentos en la base de conocimiento. Sube uno para empezar.")
    else:
        # Mostrar como tabla
        df = pd.DataFrame(docs)
        df.columns = ["Nombre del Archivo", "Fragmentos (Chunks)"]
        
        # Iterar para mostrar con botones de acción
        for doc in docs:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"📄 **{doc['filename']}**")
            with col2:
                st.caption(f"{doc['chunks']} chunks")
            with col3:
                # Botón de Descarga
                file_path = rag_service.get_document_path(doc['filename'])
                if file_path:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="📥",
                            data=f,
                            file_name=doc['filename'],
                            mime="application/pdf" if doc['filename'].endswith(".pdf") else "text/plain",
                            key=f"dl_{doc['filename']}",
                            help="Descargar documento original"
                        )
            with col4:
                if st.button("🗑️", key=f"del_{doc['filename']}", help="Eliminar documento"):
                    if rag_service.delete_document(doc['filename']):
                        st.success("Eliminado")
                        st.rerun()
                    else:
                        st.error("Error")
