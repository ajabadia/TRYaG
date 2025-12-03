import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics import render_triage_analysis as render_triage_content

def render_triage_analysis_module(df_audit_base, key_prefix="mod_triage"):
    """
    Módulo independiente de Análisis de Triaje.
    Incluye tabla con selección y tarjeta de detalles.
    """
    st.markdown("### 🏥 Análisis de Triaje")
    
    # 1. Filtros Locales
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # Filtrar
    df_filtered = df_audit_base.copy()
    if not df_filtered.empty and start_date and end_date:
        mask = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask]
        
    # 2. Barra de Acciones
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_filtered,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"triage_{date.today()}.xlsx"
    )
    
    st.divider()
    
    if df_filtered.empty:
        st.info("No hay datos.")
    else:
        # Renderizar contenido gráfico existente
        render_triage_content(df_filtered, key_prefix=f"{key_prefix}_content")
        
        st.divider()
        st.markdown("#### 📋 Detalle de Registros")
        
        # Tabla interactiva con selección
        selection = st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table"
        )
        
        # Tarjeta de Detalles
        if selection and selection.selection and selection.selection["rows"]:
            selected_index = selection.selection["rows"][0]
            # Obtener el registro del dataframe filtrado (cuidado con índices si no se resetean)
            # st.dataframe devuelve índices basados en la visualización actual si no se ordenó diferente
            # Pero mejor usar iloc sobre el df filtrado
            try:
                selected_row = df_filtered.iloc[selected_index]
                
                st.info("📝 **Detalle del Registro de Triaje**")
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**ID:** `{selected_row.get('audit_id', 'N/A')}`")
                        st.markdown(f"**Fecha:** {selected_row.get('timestamp', 'N/A')}")
                        st.markdown(f"**Nivel:** {selected_row.get('final_priority', 'N/A')}")
                    with c2:
                        st.markdown(f"**Paciente:** {selected_row.get('patient_id', 'N/A')}")
                        st.markdown(f"**Motivo:** {selected_row.get('motivo_consulta', 'N/A')}")
                    
                    st.json(selected_row.to_dict(), expanded=False)
            except Exception as e:
                st.error(f"Error al mostrar detalle: {e}")
