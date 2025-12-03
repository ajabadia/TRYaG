import streamlit as st
import pandas as pd
from db import get_database
from datetime import date, timedelta, datetime
from ui.audit_panel.components import render_date_selector, render_action_bar

@st.cache_data(ttl=60, show_spinner=False)
def load_collection_data(collection_name, date_field="timestamp", limit=1000, start_date=None, end_date=None):
    """
    Carga datos de una colección de MongoDB con filtrado básico por fecha.
    Cacheado por 60 segundos para evitar recargas masivas en cada interacción.
    """
    db = get_database()
    query = {}
    
    if start_date and end_date and date_field:
        # Convertir a datetime para consulta
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        query[date_field] = {"$gte": start_dt, "$lte": end_dt}
        
    try:
        # Intentar ordenar por fecha descendente
        cursor = db[collection_name].find(query).sort(date_field, -1).limit(limit)
        records = list(cursor)
    except:
        # Fallback si falla el sort (ej: campo no existe o índice)
        cursor = db[collection_name].find(query).limit(limit)
        records = list(cursor)
        
    if not records:
        return pd.DataFrame()
        
    df = pd.DataFrame(records)
    
    # Convertir _id a string
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)
        
    # Convertir fechas comunes
    for col in df.columns:
        if any(x in col.lower() for x in ['date', 'time', 'created', 'updated', 'start', 'end']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
                
    return df

def render_generic_log_view(
    collection_name=None,
    df=None,
    key_prefix="log",
    date_field="timestamp",
    columns_config=None,
    title=None
):
    """
    Renderiza una vista de log genérica con tabla y detalles.
    
    Args:
        collection_name (str): Nombre de la colección en MongoDB (opcional si se pasa df).
        df (pd.DataFrame): DataFrame pre-cargado (opcional).
        key_prefix (str): Prefijo para keys de Streamlit.
        date_field (str): Campo de fecha para filtrado.
        columns_config (dict): Configuración de columnas para st.dataframe.
        title (str): Título de la sección.
    """
    if title:
        st.markdown(f"##### {title}")
    elif collection_name:
        st.markdown(f"##### Log: {collection_name}")

    # --- 1. Filtros (Fechas) ---
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # --- 2. Carga de Datos ---
    if df is None and collection_name:
        # Cargar desde BD usando el filtro de fechas
        df_view = load_collection_data(
            collection_name, 
            date_field=date_field, 
            start_date=start_date, 
            end_date=end_date
        )
    elif df is not None:
        # Usar DF proporcionado y filtrar en memoria
        df_view = df.copy()
        if not df_view.empty and date_field in df_view.columns and start_date and end_date:
            try:
                mask = (df_view[date_field].dt.date >= start_date) & (df_view[date_field].dt.date <= end_date)
                df_view = df_view.loc[mask]
            except:
                pass # Si falla el filtro de fecha, mostrar todo
    else:
        st.error("Se requiere 'collection_name' o 'df'.")
        return

    # --- 3. Barra de Acciones ---
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_view,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"{collection_name or 'log'}_{date.today()}.xlsx"
    )
    
    st.divider()
    
    if df_view.empty:
        st.info("No hay registros para mostrar en este periodo.")
        return

    # --- 4. Layout Dividido (Tabla | Detalles) ---
    
    # Estado de selección
    sel_key = f"{key_prefix}_selected_idx"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = []
        
    has_selection = len(st.session_state[sel_key]) > 0
    
    if has_selection:
        col_table, col_details = st.columns([4, 6])
    else:
        col_table = st.container()
        col_details = None
        
    with col_table:
        # Configurar columnas por defecto si no hay config
        final_col_config = columns_config or {}
        
        # Ocultar columnas complejas/largas por defecto en la tabla
        # (Se verán en detalles)
        
        event = st.dataframe(
            df_view,
            column_config=final_col_config,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table"
        )
        
        # Actualizar selección
        if event.selection.rows != st.session_state[sel_key]:
            st.session_state[sel_key] = event.selection.rows
            st.rerun()

    # --- 5. Tarjeta de Detalles ---
    if has_selection and col_details:
        with col_details:
            idx_list = st.session_state[sel_key]
            if idx_list:
                try:
                    # Obtener registro seleccionado
                    # Nota: st.dataframe devuelve índice posicional relativo al DF mostrado
                    selected_row = df_view.iloc[idx_list[0]]
                    
                    st.info(f"📝 **Detalle del Registro**")
                    with st.container(border=True):
                        # Mostrar ID y Fecha si existen
                        c1, c2 = st.columns(2)
                        with c1:
                            if '_id' in selected_row:
                                st.markdown(f"**ID:** `{selected_row['_id']}`")
                            elif 'audit_id' in selected_row:
                                st.markdown(f"**ID:** `{selected_row['audit_id']}`")
                        with c2:
                            if date_field in selected_row:
                                st.markdown(f"**Fecha:** {selected_row[date_field]}")
                        
                        st.divider()
                        # JSON completo
                        st.json(selected_row.to_dict(), expanded=True)
                        
                except Exception as e:
                    st.error(f"Error al mostrar detalle: {e}")
                    st.session_state[sel_key] = []
