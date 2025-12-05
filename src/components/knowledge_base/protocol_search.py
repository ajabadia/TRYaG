import streamlit as st
from services.rag_service import get_rag_service

@st.dialog("🔍 Buscador de Protocolos", width="large")
def show_protocol_search_modal():
    """
    Muestra el modal de búsqueda de protocolos.
    """
    st.markdown("Busca rápidamente en la base de conocimiento sin usar IA generativa.")
    
    rag_service = get_rag_service()
    
    # Key única para evitar conflictos si se llama desde varios sitios
    search_query = st.text_input("Término de búsqueda:", placeholder="Ej: Esguince, Criterios Ottawa...", key="protocol_search_input_modal")
    
    if search_query:
        with st.spinner("Buscando..."):
            results = rag_service.search_documents(search_query, n_results=5)
            
        if results:
            st.success(f"Encontrados {len(results)} resultados:")
            for i, res in enumerate(results):
                with st.expander(f"📄 {res['metadata'].get('source', 'Desconocido')} (Relevancia #{i+1})", expanded=True):
                    st.markdown(f"```text\n{res['content']}\n```")
                    source_file = res['metadata'].get('source')
                    if source_file:
                        file_path = rag_service.get_document_path(source_file)
                        if file_path:
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="📥 Descargar PDF",
                                    data=f,
                                    file_name=source_file,
                                    mime="application/pdf" if source_file.endswith(".pdf") else "text/plain",
                                    key=f"dl_search_modal_{i}"
                                )
        else:
            st.warning("No se encontraron resultados.")

    st.markdown('<div class="debug-footer">src/components/knowledge_base/protocol_search.py</div>', unsafe_allow_html=True)
