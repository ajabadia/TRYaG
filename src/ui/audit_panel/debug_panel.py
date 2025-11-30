# path: src/ui/audit_panel/debug_panel.py
# Creado: 2025-11-23
# Última modificación: 2025-11-24
"""
Módulo para la visualización de la pestaña "Debug MongoDB" del panel de auditoría.
Permite inspeccionar directamente las colecciones de MongoDB.
"""
import streamlit as st
import pandas as pd
from src.db.connection import get_database
from src.utils.setup_indexes import crear_indices_patient_flow, verificar_indices_necesarios

def render_debug_panel(key_prefix="debug_panel"):
    """Renderiza el panel de depuración de MongoDB."""
    st.subheader("🔍 Inspector de MongoDB Atlas")
    st.markdown("Esta sección permite visualizar los datos crudos almacenados en las colecciones de MongoDB.")

    # --- Gestión de Índices ---
    with st.expander("🛠️ Gestión de Índices (patient_flow)", expanded=False):
        st.info("Verifica y crea los índices necesarios para el nuevo sistema de flujo de pacientes.")
        
        col_check, col_create = st.columns([1, 2])
        
        with col_check:
            if st.button("Verificar Índices", key=f"{key_prefix}_btn_verify_indexes"):
                ok, faltantes = verificar_indices_necesarios()
                if ok:
                    st.success("✅ Todos los índices necesarios existen.")
                else:
                    st.error(f"❌ Faltan {len(faltantes)} índices.")
                    for idx in faltantes:
                        st.code(idx)
        
        with col_create:
            if st.button("Crear/Reparar Índices", type="primary", key=f"{key_prefix}_btn_create_indexes"):
                ok, msg, creados = crear_indices_patient_flow()
                if ok:
                    st.success(msg)
                    if creados:
                        st.write("Índices creados:")
                        for idx in creados:
                            st.code(idx)
                else:
                    st.error(msg)
    
    st.divider()

    try:
        db = get_database()
        collections = db.list_collection_names()
        
        if not collections:
            st.warning("No se encontraron colecciones en la base de datos.")
            return

        # Crear pestañas para cada colección
        tabs = st.tabs([f":material/database: {col}" for col in collections])

        for i, collection_name in enumerate(collections):
            with tabs[i]:
                st.markdown(f"### Colección: `{collection_name}`")
                
                # Obtener conteo total
                total_docs = db[collection_name].count_documents({})
                st.info(f"Total de documentos: **{total_docs}**")
                
                # Obtener documentos recientes
                limit = st.slider(f"Límite de registros ({collection_name})", 10, 500, 50, key=f"{key_prefix}_limit_{collection_name}")
                
                # Determinar campo de ordenamiento según la colección
                sort_field = "timestamp"
                if collection_name in ['config', 'centros']:
                    sort_field = "updated_at"
                elif collection_name == 'prompts':
                    sort_field = "created_at"
                elif collection_name == 'ai_audit_logs':
                    sort_field = "timestamp_start"
                
                # Intentar ordenar, si falla usar sin ordenar
                try:
                    cursor = db[collection_name].find().sort(sort_field, -1).limit(limit)
                    records = list(cursor)
                except:
                    cursor = db[collection_name].find().limit(limit)
                    records = list(cursor)
                
                if records:
                    df = pd.DataFrame(records)
                    
                    # Convertir ObjectId a string para visualización
                    if '_id' in df.columns:
                        df['_id'] = df['_id'].astype(str)
                    
                    # Convertir timestamps si existen
                    for timestamp_field in ['timestamp', 'created_at', 'updated_at', 'timestamp_start', 'timestamp_end']:
                        if timestamp_field in df.columns:
                            df[timestamp_field] = pd.to_datetime(df[timestamp_field], errors='coerce')
                    
                    st.dataframe(df, use_container_width=True)
                    
                    with st.expander("Ver JSON crudo (primeros 5)"):
                        st.json(records[:5], expanded=False)

                    st.divider()
                    st.markdown("#### 🕵️ Inspector de Documento Individual")
                    
                    # Helper para el label del selectbox
                    def get_doc_label(doc):
                        if collection_name == 'prompts':
                            return f"{doc.get('prompt_type', 'Unknown')} ({doc.get('_id', '')})"
                        elif collection_name == 'triage_records':
                            return f"{doc.get('audit_id', 'Unknown')} - {doc.get('timestamp', '')}"
                        elif collection_name == 'file_imports_records':
                            return f"{doc.get('filename', 'Unknown')} ({doc.get('file_id', '')})"
                        elif collection_name == 'transcriptions_records':
                            return f"{doc.get('transcription_id', 'Unknown')} - {doc.get('language_name', 'N/A')}"
                        elif collection_name == 'prompt_tests':
                            return f"{doc.get('test_id', 'Unknown')} - {doc.get('prompt_type', 'N/A')}"
                        elif collection_name == 'config':
                            return f"{doc.get('key', 'Unknown')}: {str(doc.get('value', ''))[:50]}"
                        elif collection_name == 'centros':
                            salas_count = len(doc.get('salas', []))
                            return f"{doc.get('denominacion', 'Unknown')} ({doc.get('codigo', 'N/A')}) - {salas_count} salas"
                        elif collection_name == 'vital_sign_references':
                            return f"{doc.get('name', 'Unknown')} ({doc.get('unit', '')})"
                        elif collection_name == 'ai_audit_logs':
                            return f"{doc.get('call_type', 'Unknown')} | {doc.get('model_name', 'N/A')} | {doc.get('status', 'N/A')} ({doc.get('timestamp_start', '')})"
                        else:
                            return str(doc.get('_id', ''))

                    # Selectbox para elegir documento
                    selected_idx = st.selectbox(
                        f"Selecciona un documento para inspeccionar ({collection_name}):",
                        options=range(len(records)),
                        format_func=lambda i: get_doc_label(records[i]),
                        key=f"{key_prefix}_select_{collection_name}"
                    )
                    
                    # Mostrar el documento seleccionado
                    st.json(records[selected_idx], expanded=True)
                else:
                    st.warning("La colección está vacía.")

                # --- Zona de Peligro por Colección ---
                st.divider()
                st.markdown(f"#### ⚠️ Zona de Peligro - {collection_name}")
                
                # Inicializar estado de reseteo para esta colección
                reset_key = f"{key_prefix}_reset_stage_{collection_name}"
                if reset_key not in st.session_state:
                    st.session_state[reset_key] = 0

                if st.session_state[reset_key] == 0:
                    if st.button(f"🗑️ Vaciar colección `{collection_name}`", type="secondary", key=f"{key_prefix}_btn_reset_{collection_name}"):
                        st.session_state[reset_key] = 1
                        st.rerun()
                
                elif st.session_state[reset_key] == 1:
                    st.warning(f"⚠️ **¡ATENCIÓN!** Estás a punto de borrar TODOS los registros de la colección `{collection_name}`.")
                    
                    st.markdown(f"""
                    Se eliminarán permanentemente:
                    - **{total_docs}** documentos de la colección `{collection_name}`
                    
                    **Esta acción NO se puede deshacer.**
                    """)
                    
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button(f"🚨 SÍ, BORRAR TODO", type="primary", key=f"{key_prefix}_confirm_{collection_name}"):
                            try:
                                result = db[collection_name].delete_many({})
                                st.success(f"✅ Se eliminaron {result.deleted_count} documentos de `{collection_name}`")
                                st.session_state[reset_key] = 0
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al vaciar la colección: {e}")
                                st.session_state[reset_key] = 0
                    
                    with col_cancel:
                        if st.button("Cancelar", type="secondary", key=f"{key_prefix}_cancel_{collection_name}"):
                            st.session_state[reset_key] = 0
                            st.rerun()

    except Exception as e:
        st.error(f"Error al conectar con MongoDB: {e}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/audit_panel/debug_panel.py</div>', unsafe_allow_html=True)
