# src/app.py
"""Main entry point for the Triaje IA application.

This module configures Streamlit, initializes session state, ands assembles the UI.
"""

import sys
import os
import streamlit as st
import mimetypes

# FIX: Streamlit Custom Components Loading Issues
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/html', '.html')
# Force reload
from streamlit_cookies_manager import CookieManager
from ui.config_panel import mostrar_panel_configuracion
from utils.icons import get_icon_path, render_icon
from services.permissions_service import get_available_tabs
from ui.connection_status import check_database_connection
from ui.config.config_loader import load_centro_config

from components.common.user_selector import render_user_selector
from ui.main_view import mostrar_asistente_triaje


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Triaje IA - Traumatología",
    page_icon=get_icon_path("logo"),
    layout="wide",
)

# ---------------------------------------------------------------------------
# Mount Tornado Custom Routes (PDF Download / Video Upload)
# ---------------------------------------------------------------------------
try:
    from utils.tornado_server import mount_video_upload_route
    mount_video_upload_route()
except Exception as e:
    print(f"Warning: Could not mount Tornado routes: {e}")

# Gemini client configuration
# ---------------------------------------------------------------------------
try:
    # Set API key in environment for GeminiService
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    else:
        st.warning("GOOGLE_API_KEY no encontrada en secrets.toml")
except (KeyError, AttributeError):
    st.error(
        "No se ha encontrado la clave de API de Google. Asegúrate de añadirla a tu fichero .streamlit/secrets.toml"
    )

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "resultado" not in st.session_state:
    st.session_state.resultado = None

if "datos_paciente" not in st.session_state:
    st.session_state.datos_paciente = {
        "texto_medico": "",
        "edad": 40,
        "dolor": 5,
        "imagenes": [],  # archivos subidos por el usuario
        "imagenes_confirmadas_ia": [],  # imágenes enviadas a la IA
    }

# Additional flags used throughout the app
for key, default in [
    ("calificacion_humana", None),
    ("send_to_ai_checked", False),
    ("modal_image_selection", {}),
    ("analysis_complete", False),
    ("show_text_error", False),
    ("is_editing_text", True),
    ("reset_counter", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------------------
# Background Services
# ---------------------------------------------------------------------------
@st.cache_resource
def init_background_services():
    """Inicializa servicios en segundo plano (scheduler, etc.) una sola vez."""
    from services.scheduled_reports import start_scheduler
    start_scheduler()
    return True

# ---------------------------------------------------------------------------
# UI construction
# ---------------------------------------------------------------------------
def mostrar_app_principal():
    """Render the main Streamlit interface."""

    # Implementación Fase 14.2: Public Board Bypass
    # Permite acceso público a la pantalla de sala de espera sin login
    try:
        q_view = st.query_params.get("view")
        if q_view == "public_board":
            # Verificar DB (necesario para datos)
            if check_database_connection():
                 from views.public_board import render_public_board
                 render_public_board()
                 st.stop()
    except Exception as e:
        print(f"Error checking query params: {e}")
    
    # Check Authentication
    if "current_user" not in st.session_state or not st.session_state.current_user:
        from ui.login_view import render_login_view
        render_login_view()
        st.stop()
    
    # Check for Feedback Updates (Once per session)
    if "feedback_notified" not in st.session_state:
        try:
            from services.feedback_service import check_unread_updates
            username = st.session_state.current_user.get("username")
            if username:
                unread = check_unread_updates(username)
                if unread > 0:
                    st.toast(f"📢 Tienes {unread} actualizaciones en tus reportes de feedback.", icon="🔔")
            st.session_state.feedback_notified = True
        except Exception:
            pass
    
    # PWA Installer (Injects manifest and SW)
    from components.common.pwa_installer import render_pwa_installer
    render_pwa_installer()
    
    # Verify DB connection before loading anything
    if not check_database_connection():
        st.stop()

    # Initialize background services (after DB check)
    init_background_services()

    # Mount Custom Tornado Routes (The Wrapper Fix)
    try:
        from utils.tornado_server import mount_video_upload_route
        mount_video_upload_route()
    except Exception as e:
        print(f"Error mounting tornado route: {e}")

    from ui.config.config_loader import load_general_config
    if 'general_config' not in st.session_state:
        st.session_state.general_config = load_general_config()
        # Force developer mode off on reload (User Request)
        st.session_state.general_config['developer_mode'] = False
    
    centro_config = load_centro_config()

    # Load global CSS
    from utils.ui_utils import load_css
    load_css("src/assets/css/styles.css")
    
    # Check Developer Mode
    general_config = st.session_state.get('general_config', {})
    if general_config.get('developer_mode', False):
        st.markdown(
            """
            <style>
            .debug-footer {
                display: block !important;
                color: #888 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Header with logo, centre name and user menu
    col_logo, col_title, col_menu = st.columns([1, 7, 1])
    with col_logo:
        logo_path = centro_config.get("logo_path", "")
        if logo_path:
            try:
                if logo_path.startswith("http"):
                    st.markdown(
                        f'<img src="{logo_path}" style="max-height: 70px; max-width: 180px; width: auto; height: auto;">',
                        unsafe_allow_html=True
                    )
                else:
                    # Resolve path
                    resolved_path = None
                    if os.path.exists(logo_path):
                        resolved_path = logo_path
                    else:
                        if os.path.exists(os.path.abspath(logo_path)):
                             resolved_path = os.path.abspath(logo_path)
                    
                    if resolved_path:
                        from utils.ui_utils import get_image_base64
                        b64 = get_image_base64(resolved_path)
                        if b64:
                            st.markdown(
                                f'<img src="data:image/png;base64,{b64}" style="max-height: 70px; max-width: 180px; width: auto; height: auto;">',
                                unsafe_allow_html=True
                            )
                        else:
                            render_icon("logo", size=80, color="#28a745")
                    else:
                        render_icon("logo", size=80, color="#28a745")
            except Exception:
                render_icon("logo", size=80, color="#28a745")
        else:
             render_icon("logo", size=80, color="#28a745")

    with col_title:
        nombre_centro = centro_config.get(
            "denominacion", "Asistente de Triaje IA (Piloto Traumatología)"
        )
        st.title(nombre_centro)
        mensaje = centro_config.get("mensaje", "")
        if mensaje:
            st.markdown(
                f'<p class="header-message">{mensaje}</p>', unsafe_allow_html=True
            )

    # Sidebar
    render_user_selector()

    # Main tabs
    available_tabs_labels = get_available_tabs()
    
    if not available_tabs_labels:
        st.error("⛔ No tienes permisos asignados para acceder a ninguna sección del sistema.")
        st.info("Contacta con el administrador para revisar tu rol y permisos.")
        if st.button("Cerrar Sesión"):
            st.session_state.current_user = None
            st.session_state.login_selected_user = None
            st.rerun()
        st.stop()

    tabs = st.tabs(available_tabs_labels)
    
    for i, tab_label in enumerate(available_tabs_labels):
        with tabs[i]:
            if "Admisión" in tab_label:
                from ui.admission_view import mostrar_admision
                mostrar_admision()
            elif "Triaje" in tab_label:
                mostrar_asistente_triaje()
            elif "Atención Box" in tab_label:
                from ui.boxes_view import render_boxes_view
                render_boxes_view()
            elif "Sala de Espera" in tab_label:
                from ui.waiting_room_dashboard import render_waiting_room_dashboard
                render_waiting_room_dashboard()
            elif "Consulta" in tab_label:
                from ui.admission_management_view import render_admission_management_view
                render_admission_management_view()
            elif "Auditoría" in tab_label and "v2" not in tab_label.lower():
                from ui.audit_panel.main_panel_v2 import mostrar_registro_auditoria_v2
                mostrar_registro_auditoria_v2()
            elif "Control de Salas" in tab_label:
                from ui.room_orchestrator import mostrar_orquestador_salas
                mostrar_orquestador_salas()
            elif "Segunda Opinión" in tab_label:
                 from ui.modules.second_opinion_view import render_second_opinion_view
                 render_second_opinion_view()
            elif "Configuración" in tab_label:
                mostrar_panel_configuracion()

    # Footer with centre information and branding
    from components.common.footer import render_footer
    render_footer(centro_config)

# ---------------------------------------------------------------------------
# Disclaimer modal handling
# ---------------------------------------------------------------------------
cookies = CookieManager()
if not cookies.ready():
    st.stop()

disclaimer_accepted = cookies.get("disclaimer_accepted")
if not disclaimer_accepted:
    # Header of disclaimer
    st.title("Asistente de Triaje IA (Piloto Traumatología)")

    # Legal notice
    with st.container(border=True):
        c_warn_i, c_warn_t = st.columns([1, 15])
        with c_warn_i:
            render_icon("legal", size=32, color="#ffc107")
        with c_warn_t:
            st.markdown(
                """
                ### AVISO IMPORTANTE: LEER ANTES DE USAR

                * **Herramienta de Apoyo:** Este asistente es una herramienta de apoyo a la decisión clínica y **no reemplaza el juicio de un profesional sanitario cualificado.**
                * **Decisión Final Humana:** La responsabilidad de la decisión final sobre el triaje y el tratamiento del paciente recae **siempre** en el profesional sanitario.
                * **Sistema de Alto Riesgo:** Esta aplicación se considera un sistema de IA de alto riesgo según la Ley de IA de la UE. Su uso está sujeto a supervisión y auditoría.
                """
            )

    # Custom button style
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] > button {
            background-color: #28a745;
            font-size: 1.1rem;
            padding: 0.75rem 1.5rem;
            color: white;
            border: none;
            cursor: pointer;
            pass
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #218838;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("He leído y acepto los términos de uso", type="primary", use_container_width=True):
            cookies["disclaimer_accepted"] = "true"
            st.rerun()
    
    # Footer with branding
    centro_config = load_centro_config()
    from components.common.footer import render_footer
    render_footer(centro_config)
else:
    # If disclaimer already accepted, check if we need to show splash screen
    if "splash_shown" not in st.session_state:
        from ui.splash_screen import render_splash_screen
        render_splash_screen()
        st.session_state.splash_shown = True
        st.rerun()
    else:
        # Show the main app
        mostrar_app_principal()