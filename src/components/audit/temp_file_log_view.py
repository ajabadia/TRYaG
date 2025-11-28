# path: src/components/audit/temp_file_log_view.py
# Creado: 2025-11-23
# Última modificación: 2025-11-23
"""
Componente temporal para visualizar directamente los registros de ficheros importados
almacenados en MongoDB Atlas, sin aplicar filtros ni paginación. Útil para depuración.
"""
import streamlit as st
import pandas as pd

from src.db.repositories.files import get_file_imports_repository

def render_temp_file_log_view():
    """Renderiza una tabla con todos los registros de la colección `file_imports_records`.
    Si la colección está vacía muestra un mensaje informativo.
    """
    repo = get_file_imports_repository()
    # Obtener los últimos 1000 registros (ajustable)
    records = repo.get_recent(limit=1000)
    if not records:
        st.info("No hay registros de ficheros importados en MongoDB.")
        return
    df = pd.DataFrame(records)
    # Asegurarse de que la columna timestamp sea datetime para la UI
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    st.subheader("📁 Registro de Ficheros (MongoDB - Sin filtros)")
    st.dataframe(df)
