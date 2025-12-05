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
    st.subheader("Registro Completo de Decisiones")

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

    # Categorización para mejorar la navegación (Responsive)
    category = st.radio(
        "Categoría de Datos:",
        ["🏥 Actividad Clínica", "👥 Gestión & Usuarios", "🤖 Inteligencia Artificial", "⚙️ Sistema"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if category == "🏥 Actividad Clínica":
        tabs = st.tabs([
            "🏥 Triaje", "👤 Pacientes", "🌊 Flujo Pacientes", 
            "🎙️ Transcripciones", "📂 Archivos"
        ])
        
        with tabs[0]: # Triaje
            render_generic_log_view(collection_name="triage_records", key_prefix="raw_triage", title="Registros de Triaje")
        with tabs[1]: # Pacientes
            render_generic_log_view(collection_name="patients", key_prefix="raw_patients", date_field="created_at", title="Pacientes")
        with tabs[2]: # Flujo
            render_generic_log_view(collection_name="patient_flow", key_prefix="raw_flow", date_field="start_time", title="Flujo de Pacientes")
        with tabs[3]: # Transcripciones
            render_generic_log_view(collection_name="transcriptions_records", key_prefix="raw_trans", title="Log de Transcripciones")
        with tabs[4]: # Archivos
            render_generic_log_view(collection_name="file_import_records", key_prefix="raw_files", title="Log de Archivos")

    elif category == "👥 Gestión & Usuarios":
        tabs = st.tabs([
            "🔐 Usuarios", "🔑 Accesos (Login)", "👥 Personal", "📅 Turnos"
        ])
        
        with tabs[0]: # Usuarios
            render_generic_log_view(collection_name="users", key_prefix="raw_users", date_field="created_at", title="Usuarios Sistema")
        with tabs[1]: # Login
            render_generic_log_view(collection_name="login_logs", key_prefix="raw_login", date_field="timestamp", title="Accesos y Logins")
        with tabs[2]: # Personal
            render_generic_log_view(collection_name="people", key_prefix="raw_people", date_field="created_at", title="Personal (Staff)")
        with tabs[3]: # Turnos
            render_generic_log_view(collection_name="turnos", key_prefix="raw_turnos", date_field="fecha", title="Turnos")

    elif category == "🤖 Inteligencia Artificial":
        tabs = st.tabs([
            "🤖 AI Audit", "🧠 AI Models", "🧪 Tests Prompts", 
            "📜 Versiones Prompts", "🐛 Feedback"
        ])
        
        with tabs[0]: # AI Audit
            render_generic_log_view(collection_name="ai_audit_logs", key_prefix="raw_ai_audit", date_field="timestamp_start", title="Auditoría IA")
        with tabs[1]: # AI Models
            render_generic_log_view(collection_name="ai_models", key_prefix="raw_ai_models", date_field="created_at", title="Modelos IA")
        with tabs[2]: # Tests Prompts
            render_generic_log_view(collection_name="prompt_tests", key_prefix="raw_prompt_test", date_field="created_at", title="Tests de Prompts")
        with tabs[3]: # Versiones
            render_prompt_log_final(key_prefix="raw_prompts_special")
        with tabs[4]: # Feedback
            render_generic_log_view(collection_name="feedback_reports", key_prefix="raw_feedback", title="Reportes de Feedback")

    elif category == "⚙️ Sistema":
        tabs = st.tabs([
            "📋 Auditoría General", "🔔 Notificaciones"
        ])
        
        with tabs[0]: # Auditoría General
            render_generic_log_view(collection_name="audit_log", key_prefix="raw_audit", title="Log de Auditoría")
        with tabs[1]: # Notificaciones
            render_generic_log_view(collection_name="notifications", key_prefix="raw_notif", date_field="created_at", title="Notificaciones")

    st.markdown('<div class="debug-footer">src/ui/audit_panel/raw_data_panel_v2.py</div>', unsafe_allow_html=True)
