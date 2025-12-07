# path: src/ui/audit_panel/main_panel_v2.py
"""
Módulo principal del panel de auditoría (Versión Modular V2).
"""

from datetime import date, datetime, timedelta
import streamlit as st
import pandas as pd
from .raw_data_panel_v2 import mostrar_panel_datos_brutos_v2
from .analysis_panel_modular import mostrar_panel_analisis_modular
from .debug_panel_modular import render_debug_panel_modular
from db.repositories.audit import get_audit_repository
from db.repositories.files import get_file_imports_repository
from db.repositories.transcriptions import get_transcriptions_repository

# Constantes
PAGE_SIZE = 25



def mostrar_registro_auditoria_v2():
    """Muestra el panel de auditoría V2."""
    st.header("📋 Panel de Auditoría y Supervisión")

    if "num_audit_records_to_show" not in st.session_state:
        st.session_state.num_audit_records_to_show = PAGE_SIZE

    tab_datos, tab_analisis, tab_predicciones, tab_debug, tab_docs = st.tabs([
        "📉 Datos en Bruto",
        "📈 Análisis Gráfico",
        "🧠 Predicciones IA",
        "🛠️ Debug MongoDB",
        "📚 Documentación"
    ])

    try:
        # Importar loading indicator
        from services.feedback_service import get_feedback_reports
        
        # Cargar repositorios y datos con indicador de carga
        # Cargar repositorios y datos con indicador de carga
        @st.cache_data(ttl=60, show_spinner=False)
        def load_audit_data_v2():
            audit_repo = get_audit_repository()
            files_repo = get_file_imports_repository()
            trans_repo = get_transcriptions_repository()
            
            return (
                audit_repo.get_recent(limit=1000),
                files_repo.get_recent(limit=1000),
                trans_repo.get_recent(limit=1000),
                get_feedback_reports(limit=1000)
            )

        audit_records, files_records, trans_records, feedback_records = load_audit_data_v2()

        # Convertir a DataFrames
        df_audit_base = pd.DataFrame(audit_records)
        df_files = pd.DataFrame(files_records)
        df_trans = pd.DataFrame(trans_records)
        df_feedback = pd.DataFrame(feedback_records)

        # Garantizar columnas mínimas
        if df_audit_base.empty:
            df_audit_base = pd.DataFrame(columns=["timestamp", "decision_humana", "detalles"])
        if df_files.empty:
            df_files = pd.DataFrame(columns=["timestamp", "file_name", "file_type", "file_md5"])
        elif "file_md5" not in df_files.columns:
            df_files["file_md5"] = None
        if df_trans.empty:
            df_trans = pd.DataFrame(columns=["timestamp", "original_text"])
        if df_feedback.empty:
            df_feedback = pd.DataFrame(columns=["timestamp", "type", "module", "status"])

        # Debug panel (Modular)
        with tab_debug:
            render_debug_panel_modular(key_prefix="v2_debug_mod")
            
        # Documentation Panel
        with tab_docs:
            st.markdown("### 📚 Documentación Pública")
            import os
            docs_dir = "docs/public"
            
            if not os.path.exists(docs_dir):
                st.warning(f"Directorio no encontrado: {docs_dir}")
                os.makedirs(docs_dir, exist_ok=True) # Create if missing for next time
            else:
                files = os.listdir(docs_dir)
                files = [f for f in files if os.path.isfile(os.path.join(docs_dir, f))]
                
                if not files:
                    st.info("No hay documentos disponibles en este momento.")
                else:
                    st.markdown("Documentos disponibles para descarga:")
                    for f_name in files:
                        f_path = os.path.join(docs_dir, f_name)
                        with open(f_path, "rb") as f_obj:
                            btn_label = f"⬇️ Descargar {f_name}"
                            st.download_button(
                                label=btn_label,
                                data=f_obj,
                                file_name=f_name,
                                mime="application/octet-stream"
                            )

        # Procesar timestamps
        if "timestamp" in df_audit_base.columns:
            df_audit_base["timestamp"] = pd.to_datetime(df_audit_base["timestamp"], errors="coerce")
            df_audit_base.dropna(subset=["timestamp"], inplace=True)
            df_audit_base.sort_values(by="timestamp", ascending=False, inplace=True)

            # Expandir detalles si existen
            if "detalles" in df_audit_base.columns:
                detalles_df = pd.json_normalize(df_audit_base["detalles"])
                for col in detalles_df.columns:
                    if col not in df_audit_base.columns:
                        df_audit_base[col] = detalles_df[col]
            
            # Asegurar que existe audit_id (usar _id si no existe)
            if "audit_id" not in df_audit_base.columns:
                if "_id" in df_audit_base.columns:
                    df_audit_base["audit_id"] = df_audit_base["_id"].astype(str)
                else:
                    # Generar IDs temporales si no hay _id
                    df_audit_base["audit_id"] = [f"AUD-{i:04d}" for i in range(len(df_audit_base))]


        if not df_files.empty and "timestamp" in df_files.columns:
            df_files["timestamp"] = pd.to_datetime(df_files["timestamp"], errors="coerce")
        if not df_trans.empty and "timestamp" in df_trans.columns:
            df_trans["timestamp"] = pd.to_datetime(df_trans["timestamp"], errors="coerce")
        if not df_feedback.empty and "timestamp" in df_feedback.columns:
            df_feedback["timestamp"] = pd.to_datetime(df_feedback["timestamp"], errors="coerce")

        # Parámetros de URL
        params = st.query_params
        def get_date_from_params(param_name, default_date):
            try:
                return date.fromisoformat(params[param_name])
            except (KeyError, ValueError):
                return default_date

        # Rango global de fechas (Solo para Análisis Gráfico por ahora, ya que Datos V2 es modular)
        if not df_audit_base.empty:
            min_date = df_audit_base["timestamp"].min().date()
            max_date = df_audit_base["timestamp"].max().date()
            if min_date == max_date:
                max_date = min_date + timedelta(days=1)
        else:
            min_date = date(2020, 1, 1)
            max_date = date.today()

        default_start_analisis = get_date_from_params("analisis_start", min_date)
        default_end_analisis = get_date_from_params("analisis_end", max_date)

        # Decisiones únicas
        decisiones_uniques = []
        if "decision_humana" in df_audit_base.columns:
            decisiones_uniques = df_audit_base["decision_humana"].dropna().unique().tolist()
        default_decisions = params.get_all("decisiones") or decisiones_uniques

        # Renderizar paneles
        with tab_analisis:
            mostrar_panel_analisis_modular(
                df_audit_base,
                df_files,
                df_trans,
                df_feedback,
                key_prefix="v2_analisis_mod",
            )
            
        with tab_predicciones:
            from ui.ml_predictions_panel import render_ml_predictions_panel
            render_ml_predictions_panel()

        with tab_datos:
            mostrar_panel_datos_brutos_v2(
                df_audit_base,
                df_files,
                df_trans,
                df_feedback
            )

    except Exception as e:
        st.error(f"Error al cargar datos de auditoría: {e}")

    st.markdown('<div class="debug-footer">src/ui/audit_panel/main_panel_v2.py</div>', unsafe_allow_html=True)
