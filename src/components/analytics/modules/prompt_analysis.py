import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics.prompt_analysis import render_prompt_analysis as render_prompt_content
# Nota: render_prompt_analysis originalmente hacía su propia query. 
# Para ser modular y consistente, deberíamos pasarle el rango de fechas o refactorizarlo.
# Revisando el código original, render_prompt_analysis no recibe argumentos de fecha, consulta todo.
# Vamos a envolverlo pero idealmente deberíamos modificar el componente base para aceptar fechas.
# Por ahora, mantenemos la estructura pero añadimos el selector aunque no filtre internamente el componente legacy,
# O mejor, re-implementamos la carga aquí para filtrar.

from db import get_database
import pandas as pd

def render_prompt_analysis_module(key_prefix="mod_prompts"):
    """
    Módulo independiente de Análisis de Prompts.
    """
    st.markdown("### 📜 Análisis de Prompts")
    
    # 1. Filtros
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # Cargar y Filtrar Datos manualmente aquí (ya que el componente legacy era opaco)
    db = get_database()
    cursor = db.prompts.find({})
    df_prompts = pd.DataFrame(list(cursor))
    
    if not df_prompts.empty:
        if 'created_at' in df_prompts.columns:
            df_prompts['created_at'] = pd.to_datetime(df_prompts['created_at'])
            if start_date and end_date:
                mask = (df_prompts['created_at'].dt.date >= start_date) & (df_prompts['created_at'].dt.date <= end_date)
                df_prompts = df_prompts.loc[mask]
    
    # 2. Acciones
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_prompts,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"prompts_{date.today()}.xlsx"
    )
    
    st.divider()
    
    if df_prompts.empty:
        st.info("No hay prompts registrados en este periodo.")
    else:
        # Mostrar métricas básicas
        st.metric("Total Prompts", len(df_prompts))
        
        # Tabla Detallada
        st.markdown("#### 📋 Listado de Prompts")
        
        # Ocultar contenido largo para la tabla
        df_display = df_prompts.copy()
        if 'content' in df_display.columns:
            df_display['content_preview'] = df_display['content'].astype(str).str[:50] + "..."
            cols = [c for c in df_display.columns if c != 'content']
        else:
            cols = df_display.columns
            
        selection = st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table"
        )
        
        if selection and selection.selection and selection.selection["rows"]:
            idx = selection.selection["rows"][0]
            try:
                row = df_prompts.iloc[idx] # Usar el df original con contenido completo
                st.info(f"📝 **Detalle Prompt: {row.get('prompt_type', 'N/A')}**")
                
                with st.container(border=True):
                    st.text_area("Contenido", row.get('content', ''), height=300)
                    st.json(row.to_dict(), expanded=False)
            except:
                pass
