import streamlit as st
import pandas as pd
from db import get_database
from datetime import datetime, date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar

def render_collection_inspector(collection_name, key_prefix, date_field="timestamp", default_limit=100):
    """
    Módulo genérico para inspeccionar una colección de MongoDB.
    Incluye:
    - Selector de fechas propio.
    - Tabla con selección.
    - Tarjeta de detalles del registro seleccionado.
    - Barra de acciones (Refrescar, CSV, Excel, PDF).
    - Zona de peligro (borrado).
    """
    st.markdown(f"### 🗄️ Colección: `{collection_name}`")
    
    db = get_database()
    
    # --- 1. Filtros (Fechas) ---
    # Determinar rango por defecto (últimos 30 días o todo si es pequeño)
    # Para optimizar, no consultamos todo el rango inicial, usamos defaults
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    # Renderizar selector de fechas
    # Nota: min_date/max_date podrían consultarse, pero para evitar latencia usamos un rango amplio fijo
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=f"{key_prefix}_{collection_name}"
    )
    
    # --- 2. Consulta de Datos ---
    query = {}
    if date_field:
        # Construir query de fecha si el campo existe
        # Necesitamos saber si el campo es string o date en la BD. Asumimos ISODate o String ISO.
        # Para ser genéricos, intentamos filtrar en memoria si la colección no es gigante,
        # o hacemos query si es soportado. Por simplicidad y seguridad en este inspector genérico:
        # Hacemos query a Mongo.
        
        # Ajustar fechas para cubrir el día completo
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        query[date_field] = {"$gte": start_dt, "$lte": end_dt}

    # Límite de registros
    limit = st.slider(f"Límite de registros ({collection_name})", 10, 1000, default_limit, key=f"{key_prefix}_limit_{collection_name}")
    
    try:
        # Intentar ordenar por fecha descendente
        cursor = db[collection_name].find(query).sort(date_field, -1).limit(limit)
        records = list(cursor)
    except Exception as e:
        st.warning(f"No se pudo filtrar por fecha en el campo '{date_field}' o la consulta falló. Mostrando últimos registros.")
        cursor = db[collection_name].find().limit(limit)
        records = list(cursor)

    total_docs = db[collection_name].count_documents(query)
    st.caption(f"Mostrando {len(records)} de {total_docs} documentos encontrados en el rango.")

    if not records:
        st.info("No hay datos para mostrar en este rango.")
        return

    df = pd.DataFrame(records)
    
    # Convertir _id a string
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)
        
    # Convertir fechas
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower() or "created" in col.lower() or "updated" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass

    # --- 3. Barra de Acciones ---
    def pdf_generator():
        from utils.pdf_utils import PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Reporte de Colección: {collection_name}', ln=1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1)
        pdf.cell(0, 10, f"Registros: {len(df)}", ln=1)
        pdf.ln(5)
        # Tabla simple (solo algunas columnas clave para que quepa)
        cols_to_print = list(df.columns)[:5] 
        for i, row in df.iterrows():
            line = " | ".join([str(row[c])[:20] for c in cols_to_print])
            pdf.multi_cell(0, 6, line, border=1)
        return bytes(pdf.output())

    render_action_bar(
        key_prefix=f"{key_prefix}_{collection_name}_actions",
        df=df,
        on_refresh=lambda: st.rerun(),
        pdf_generator=pdf_generator,
        excel_filename=f"{collection_name}_{date.today()}.xlsx"
    )
    
    st.divider()

    # --- 4. Tabla con Selección y Tarjeta de Detalles ---
    
    # Configurar columnas para la tabla (ocultar _id si hay muchas columnas, o ponerlo al final)
    # Usamos st.dataframe con selection_mode
    
    st.markdown("##### 📋 Registros")
    
    # Evento de selección
    selection = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=f"{key_prefix}_table_{collection_name}"
    )
    
    # --- 5. Tarjeta de Detalles ---
    if selection and selection.selection and selection.selection["rows"]:
        selected_index = selection.selection["rows"][0]
        selected_record = records[selected_index]
        
        st.info("📝 **Detalle del Registro Seleccionado**")
        
        with st.container(border=True):
            # Cabecera del detalle
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**ID:** `{selected_record.get('_id', 'N/A')}`")
            with c2:
                st.caption("JSON View")
            
            # Mostrar JSON completo
            st.json(selected_record, expanded=True)
            
    # --- 6. Zona de Peligro ---
    with st.expander(f"⚠️ Zona de Peligro ({collection_name})", expanded=False):
        st.warning("Acciones destructivas.")
        if st.button(f"🗑️ Eliminar TODOS los registros mostrados ({len(records)})", key=f"{key_prefix}_del_{collection_name}"):
            # Lógica de borrado (simulada o real con confirmación extra)
            st.error("Funcionalidad de borrado masivo protegida. Implementar confirmación doble si es necesario.")

