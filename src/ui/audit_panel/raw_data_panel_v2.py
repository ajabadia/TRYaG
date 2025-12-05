# path: src/ui/audit_panel/raw_data_panel_v2.py
"""
Módulo orquestador para la visualización de la pestaña "Datos en Bruto" (Versión Modular V2).
Cada pestaña gestiona sus propios filtros y fechas mediante el componente genérico.
"""

import streamlit as st
import pandas as pd
from components.audit.generic_log_view import render_generic_log_view
from components.audit.prompt_log import render_prompt_log_final

def mostrar_panel_datos_brutos_v2(df_audit_base, df_files, df_trans, df_feedback):
    """
    Renderiza la pestaña "Datos en Bruto" V2.
    Utiliza el componente genérico para todas las colecciones solicitadas.
    """
    st.subheader("Registro Completo de Decisiones (Modular)")

    # Lista de pestañas solicitadas
    # 1. audit_log
    # 2. file_import_records
    # 3. transcriptions_records
    # 4. feedback_reports
    # 5. ai_audit_logs
    # 6. ai_models
    # 7. notifications
    # 8. patient_flow
    # 9. patients
    # 10. people
    # 11. prompt_test
    # 12. triage_records
    # 13. turnos
    # 14. users
    # + Log de Prompts (Especial)

    tabs = st.tabs([
        "📋 Auditoría General",
        "📂 Archivos",
        "🎙️ Transcripciones",
        "🐛 Feedback",
        "🤖 AI Audit",
        "🧠 AI Models",
        "🔔 Notificaciones",
        "🌊 Flujo Pacientes",
        "👤 Pacientes",
        "👥 Personal",
        "🧪 Tests Prompts",
        "🏥 Triaje",
        "📅 Turnos",
        "🔐 Usuarios",
        "🔑 Accesos (Login)",
        "📜 Versiones Prompts" # Mantenemos el especial al final
    ])

    # 1. audit_log
    with tabs[0]:
        render_generic_log_view(collection_name="audit_log", key_prefix="raw_audit", title="Log de Auditoría")

    # 2. file_import_records
    with tabs[1]:
        render_generic_log_view(collection_name="file_import_records", key_prefix="raw_files", title="Log de Archivos")

    # 3. transcriptions_records
    with tabs[2]:
        render_generic_log_view(collection_name="transcriptions_records", key_prefix="raw_trans", title="Log de Transcripciones")

    # 4. feedback_reports
    with tabs[3]:
        render_generic_log_view(collection_name="feedback_reports", key_prefix="raw_feedback", title="Reportes de Feedback")

    # 5. ai_audit_logs
    with tabs[4]:
        render_generic_log_view(collection_name="ai_audit_logs", key_prefix="raw_ai_audit", date_field="timestamp_start", title="Auditoría IA")

    # 6. ai_models
    with tabs[5]:
        render_generic_log_view(collection_name="ai_models", key_prefix="raw_ai_models", date_field="created_at", title="Modelos IA")

    # 7. notifications
    with tabs[6]:
        render_generic_log_view(collection_name="notifications", key_prefix="raw_notif", date_field="created_at", title="Notificaciones")

    # 8. patient_flow
    with tabs[7]:
        render_generic_log_view(collection_name="patient_flow", key_prefix="raw_flow", date_field="start_time", title="Flujo de Pacientes")

    # 9. patients
    with tabs[8]:
        render_generic_log_view(collection_name="patients", key_prefix="raw_patients", date_field="created_at", title="Pacientes")

    # 10. people
    with tabs[9]:
        render_generic_log_view(collection_name="people", key_prefix="raw_people", date_field="created_at", title="Personal (Staff)")

    # 11. prompt_test
    with tabs[10]:
        render_generic_log_view(collection_name="prompt_tests", key_prefix="raw_prompt_test", date_field="created_at", title="Tests de Prompts")

    # 12. triage_records
    with tabs[11]:
        render_generic_log_view(collection_name="triage_records", key_prefix="raw_triage", title="Registros de Triaje")

    # 13. turnos
    with tabs[12]:
        render_generic_log_view(collection_name="turnos", key_prefix="raw_turnos", date_field="fecha", title="Turnos")

    # 14. users
    with tabs[13]:
        render_generic_log_view(collection_name="users", key_prefix="raw_users", date_field="created_at", title="Usuarios Sistema")

    # 15. Login Logs (Nuevo)
    with tabs[14]:
        render_generic_log_view(collection_name="login_logs", key_prefix="raw_login", date_field="timestamp", title="Accesos y Logins")

    # 16. Log de Prompts (Especial)
    with tabs[15]:
        render_prompt_log_final(key_prefix="raw_prompts_special")

    st.markdown('<div class="debug-footer">src/ui/audit_panel/raw_data_panel_v2.py</div>', unsafe_allow_html=True)
