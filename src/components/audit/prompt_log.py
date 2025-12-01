# path: src/components/audit/prompt_log.py
# Creado: 2025-11-23
# Actualizado: 2025-11-23 - Fix para MongoDB
"""
Componente para la visualización del log de versiones de prompts.
"""
import streamlit as st
import pandas as pd
from core.prompt_manager import PromptManager

def load_prompts_dataframe():
    """
    Carga los prompts y los aplana en un DataFrame para visualización.
    """
    pm = PromptManager()
    
    # Obtener todos los prompts usando el repositorio
    try:
        all_prompts = pm.repo.get_all_prompts() if pm.repo else []
    except:
        all_prompts = []
    
    data = []
    for prompt_doc in all_prompts:
        prompt_type = prompt_doc.get("prompt_type", "unknown")
        active_ver = prompt_doc.get("active_version")
        versions = prompt_doc.get("versions", [])
        
        for version in versions:
            ver_id = version.get("version_id", "N/A")
            created_at = version.get("created_at")
            updated_at = version.get("updated_at")
            
            # Convertir datetime a string si es necesario
            if hasattr(created_at, 'isoformat'):
                created_at = created_at.isoformat()
            if hasattr(updated_at, 'isoformat'):
                updated_at = updated_at.isoformat()
            
            row = {
                "prompt_type": prompt_type,
                "version_id": ver_id,
                "status": version.get("status", "unknown"),
                "author": version.get("author", "unknown"),
                "created_at": created_at,
                "updated_at": updated_at,
                "notes": version.get("notes", ""),
                "content": version.get("content", ""),
                "is_active": (ver_id == active_ver)
            }
            data.append(row)
            
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    # Fix: Handle ISO8601 with microseconds using format='mixed'
    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce')
    if 'updated_at' in df.columns:
        df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed', errors='coerce')
    
    df.sort_values(by='created_at', ascending=False, inplace=True)
    return df

def render_prompt_details(selected_records):
    """
    Renderiza el detalle de los prompts seleccionados (Card View).
    """
    st.markdown("### Detalle del Prompt")
    if len(selected_records) > 1:
        st.info("Seleccione un solo registro para ver el detalle completo.", icon=":material/info:")
    
    for _, row in selected_records.iterrows():
        with st.container(border=True):
            # Cabecera con Icono de Estado
            status_icon = "🟢" if row['status'] == 'active' else "📝" if row['status'] == 'draft' else "⚫"
            st.markdown(f"### {status_icon} {row['prompt_type']} - `{row['version_id']}`")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Autor:** {row['author']}")
                st.markdown(f"**Creado:** {row['created_at'].strftime('%d/%m/%Y %H:%M')}")
            with col2:
                st.markdown(f"**Estado:** `{row['status']}`")
                if pd.notna(row['updated_at']):
                     st.markdown(f"**Actualizado:** {row['updated_at']}")
            
            if row['notes']:
                st.info(f"**Notas:** {row['notes']}")
            
            st.divider()
            st.markdown("**Contenido:**")
            st.code(row['content'], language="json" if row['prompt_type'] == 'triage_sim' else "markdown")


def render_prompt_log_final(key_prefix="prompt_log"):
    st.markdown("##### Historial de Versiones de Prompts")
    
    df_prompts = load_prompts_dataframe()
    
    if df_prompts.empty:
        st.info("No hay historial de prompts disponible.")
        return

    # --- Filtros ---
    # --- Filtros ---
    from ui.audit_panel.components import render_action_bar, render_date_selector
    from datetime import date, timedelta

    # Determinar rango de fechas
    if not df_prompts.empty:
        min_date = df_prompts['created_at'].min().date()
        max_date = df_prompts['created_at'].max().date()
        if min_date == max_date:
            max_date = min_date + timedelta(days=1)
    else:
        min_date = date(2020, 1, 1)
        max_date = date.today()

    # Selector de Fechas
    start_date, end_date = render_date_selector(
        min_date, max_date,
        min_date, max_date, # Default to full range
        key_prefix=key_prefix
    )

    # Aplicar filtro de fechas
    if start_date and end_date:
        mask = (df_prompts['created_at'].dt.date >= start_date) & (df_prompts['created_at'].dt.date <= end_date)
        df_prompts = df_prompts.loc[mask]

    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_prompts,
        on_refresh=lambda: st.rerun(),
        excel_filename="prompt_log.xlsx"
    )
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        types = ["Todos"] + sorted(df_prompts['prompt_type'].unique().tolist())
        sel_type = st.selectbox("Filtrar por Tipo", types, key=f"{key_prefix}_filter_prompt_type")
    
    with col_f2:
        statuses = ["Todos"] + sorted(df_prompts['status'].unique().tolist())
        sel_status = st.selectbox("Filtrar por Estado", statuses, key=f"{key_prefix}_filter_prompt_status")

    # Aplicar filtros
    df_view = df_prompts.copy()
    if sel_type != "Todos":
        df_view = df_view[df_view['prompt_type'] == sel_type]
    if sel_status != "Todos":
        df_view = df_view[df_view['status'] == sel_status]

    # --- Estado de Selección ---
    if f'{key_prefix}_selected_prompt_idx' not in st.session_state:
        st.session_state[f'{key_prefix}_selected_prompt_idx'] = []

    # --- Layout Dividido: Tabla (Izquierda) | Detalles (Derecha) ---
    has_selection = len(st.session_state[f'{key_prefix}_selected_prompt_idx']) > 0
    
    if has_selection:
        col_table, col_details = st.columns([4, 6])
    else:
        col_table = st.container()
        col_details = None
        
    with col_table:
        column_config = {
            "prompt_type": "Tipo",
            "version_id": "Versión",
            "status": "Estado",
            "author": "Autor",
            "created_at": st.column_config.DatetimeColumn("Creado", format="DD/MM/YYYY HH:mm"),
            "notes": "Notas",
            "content": st.column_config.TextColumn("Contenido", width="large"),
            "updated_at": st.column_config.DatetimeColumn("Actualizado", format="DD/MM/YYYY HH:mm"),
            "is_active": st.column_config.CheckboxColumn("Activo")
        }
        
        event = st.dataframe(
            df_view,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table"
        )
        
        # Actualizar estado para el próximo rerun
        current_selection = event.selection.rows
        if current_selection != st.session_state[f'{key_prefix}_selected_prompt_idx']:
            st.session_state[f'{key_prefix}_selected_prompt_idx'] = current_selection
            st.rerun() # Forzar recarga para ajustar layout

    if has_selection and col_details:
        with col_details:
            selected_indices = st.session_state[f'{key_prefix}_selected_prompt_idx']
            if selected_indices:
                try:
                    selected_records = df_view.iloc[selected_indices]
                    with st.container(height=800, border=False):
                        render_prompt_details(selected_records)
                except IndexError:
                    st.session_state[f'{key_prefix}_selected_prompt_idx'] = []
                    st.rerun()
