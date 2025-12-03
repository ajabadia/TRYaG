import streamlit as st
import pandas as pd
import io
from datetime import datetime

def render_action_bar(key_prefix, df=None, on_refresh=None, pdf_generator=None, excel_filename="data.xlsx", share_params=None):
    """
    Renderiza una barra de acciones estandarizada: Refrescar, Descargar CSV/Excel, PDF, Compartir.
    
    Args:
        key_prefix (str): Prefijo único para las keys de los botones.
        df (pd.DataFrame): DataFrame con los datos a exportar.
        on_refresh (callable): Función a ejecutar al pulsar refrescar.
        pdf_generator (callable): Función que devuelve bytes del PDF.
        excel_filename (str): Nombre del archivo Excel.
        share_params (dict): Parámetros para la URL al compartir.
    """
    col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1.5, 2, 2])
    
    # 1. Refrescar
    with col1:
        if st.button("Refrescar", icon="🔄", key=f"{key_prefix}_refresh"):
            if on_refresh:
                on_refresh()
            else:
                st.rerun()

    # 2. CSV
    with col2:
        if df is not None and not df.empty:
            csv_data = df.to_csv(index=False, sep=';', encoding='utf-8')
            st.download_button(
                "CSV", 
                csv_data, 
                f"{excel_filename.replace('.xlsx', '.csv')}", 
                'text/csv', 
                icon="📥",
                key=f"{key_prefix}_csv"
            )
        else:
            st.button("CSV", disabled=True, icon="📥", key=f"{key_prefix}_csv_disabled")

    # 3. Excel
    with col3:
        if df is not None and not df.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                "Excel", 
                buffer.getvalue(), 
                excel_filename, 
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                icon="📥",
                key=f"{key_prefix}_excel"
            )
        else:
            st.button("Excel", disabled=True, icon="📥", key=f"{key_prefix}_excel_disabled")

    # 4. Compartir
    with col4:
        if st.button("Compartir", icon="📤", key=f"{key_prefix}_share", use_container_width=True):
            if share_params:
                st.query_params.clear()
                for k, v in share_params.items():
                    st.query_params[k] = v
                st.success("¡Enlace copiado!")
            else:
                st.info("Función de compartir no configurada")

    # 5. PDF
    with col5:
        if pdf_generator and df is not None and not df.empty:
            if st.button("Informe PDF", icon="📄", key=f"{key_prefix}_pdf_btn", use_container_width=True):
                pdf_bytes = pdf_generator()
                st.download_button(
                    "Descargar PDF",
                    pdf_bytes,
                    f"report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    "application/pdf",
                    key=f"{key_prefix}_pdf_dl"
                )
        else:
            st.button("Informe PDF", disabled=True, icon="📄", key=f"{key_prefix}_pdf_disabled", use_container_width=True)

def render_filters(df, columns_to_filter, key_prefix):
    """
    Renderiza filtros dinámicos para un DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame a filtrar.
        columns_to_filter (list): Lista de nombres de columnas para generar filtros.
        key_prefix (str): Prefijo para keys.
        
    Returns:
        pd.DataFrame: DataFrame filtrado.
    """
    if df is None or df.empty:
        return df
        
    with st.expander("🔍 Filtros Avanzados"):
        cols = st.columns(len(columns_to_filter))
        filters = {}
        
        for i, col_name in enumerate(columns_to_filter):
            if col_name in df.columns:
                with cols[i]:
                    options = df[col_name].dropna().unique().tolist()
                    filters[col_name] = st.multiselect(
                        f"Filtrar por {col_name}",
                        options,
                        key=f"{key_prefix}_filter_{col_name}"
                    )
        
        # Aplicar filtros
        df_filtered = df.copy()
        for col_name, selected_values in filters.items():
            if selected_values:
                df_filtered = df_filtered[df_filtered[col_name].isin(selected_values)]
                
        return df_filtered

def calculate_date_range(dataframes):
    """
    Calcula el rango global de fechas a partir de una lista de DataFrames.
    
    Args:
        dataframes (list): Lista de DataFrames.
        
    Returns:
        tuple: (min_date, max_date)
    """
    all_dates = []
    for df in dataframes:
        if df is not None and not df.empty and "timestamp" in df.columns:
            # Asegurar datetime
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                 try:
                    dates = pd.to_datetime(df["timestamp"], errors='coerce').dropna().tolist()
                    all_dates.extend(dates)
                 except:
                     pass
            else:
                all_dates.extend(df["timestamp"].dropna().tolist())

    if all_dates:
        min_date = min(all_dates).date()
        max_date = max(all_dates).date()
        
        # Asegurar que el rango incluye "hoy"
        if max_date < datetime.now().date():
            max_date = datetime.now().date()
            
        if min_date == max_date:
            max_date = min_date + pd.Timedelta(days=1)
    else:
        min_date = datetime(2020, 1, 1).date()
        max_date = datetime.now().date()
        
    return min_date, max_date

def render_date_selector(min_date, max_date, default_start, default_end, key_prefix):
    """
    Renderiza selectores de fecha estandarizados.
    
    Args:
        min_date (date): Fecha mínima permitida.
        max_date (date): Fecha máxima permitida.
        default_start (date): Fecha inicial por defecto.
        default_end (date): Fecha final por defecto.
        key_prefix (str): Prefijo para keys de Streamlit.
        
    Returns:
        tuple: (start_date, end_date)
    """
    col1, col2 = st.columns(2)
    
    # Asegurar que los defaults están dentro del rango
    start_val = default_start
    if start_val < min_date: start_val = min_date
    if start_val > max_date: start_val = max_date
    
    end_val = default_end
    if end_val < min_date: end_val = min_date
    if end_val > max_date: end_val = max_date
    
    if start_val > end_val:
        start_val = end_val

    with col1:
        start_date = st.date_input(
            "Desde",
            value=start_val,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            key=f"{key_prefix}_date_start"
        )
        
    with col2:
        end_date = st.date_input(
            "Hasta",
            value=end_val,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            key=f"{key_prefix}_date_end"
        )
        
    return start_date, end_date

    st.markdown('<div class="debug-footer">src/ui/audit_panel/components.py</div>', unsafe_allow_html=True)
