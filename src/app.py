# src/app.py
"""Main entry point for the Triaje IA application.

This module configures Streamlit, initializes session state, and assembles the UI.
"""

import sys
import os
import streamlit as st
from streamlit_cookies_manager import CookieManager

# Ensure the project root is in the Python path before any imports
root_dir = os.path.dirname(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.permissions_service import get_available_tabs
from services.gemini_client import configure_gemini
from ui.connection_status import check_database_connection
from ui.config_panel import load_centro_config
from ui.loading_indicator import render_loading_container
from components.common.user_selector import render_user_selector
import ui.main_view
from ui.config_panel import mostrar_panel_configuracion
from utils.icons import get_icon_path, render_icon

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Triaje IA - Traumatología",
    page_icon=get_icon_path("logo"),
    layout="wide",
)

# PWA Support and UI Transition Improvements
st.markdown(
    """
    <script>
        // Inject Manifest
        const link = document.createElement('link');
        link.rel = 'manifest';
        link.href = 'app/static/manifest.json';
        document.head.appendChild(link);

        // Register Service Worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('app/static/service-worker.js').then(function(registration) {
                    console.log('ServiceWorker registration successful with scope: ', registration.scope);
                }, function(err) {
                    console.log('ServiceWorker registration failed: ', err);
                });
            });
        }

        // UI Transition Handler
        document.addEventListener('DOMContentLoaded', function() {
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length) {
                        const buttons = document.querySelectorAll('button');
                        buttons.forEach(btn => {
                            if (!btn.dataset.listenerAttached) {
                                btn.addEventListener('click', function() {
                                    const appContainer = document.querySelector('.stApp');
                                    if (appContainer) {
                                        appContainer.classList.add('app-transitioning');
                                    }
                                });
                                btn.dataset.listenerAttached = 'true';
                            }
                        });
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    </script>
    <style>
        /* Transition effect */
        .app-transitioning {
            opacity: 0.6;
            pointer-events: none;
            transition: opacity 0.2s ease-out;
            filter: blur(1px);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Gemini client configuration
# ---------------------------------------------------------------------------
try:
    success, error_msg = configure_gemini(st.secrets["GOOGLE_API_KEY"])
    if not success:
        st.error(f"Error al configurar la API de Gemini: {error_msg}")
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
        /* Reduce top spacing of the app */
        .main > div {
            padding-top: 1rem;
        }
        /* Reduce header spacing */
        header {
            padding-top: 0rem !important;
        }
        /* Reduce space between title and message */
        .header-message {
            margin-top: -15px;
            font-size: 0.9rem;
            color: #666;
        }
        /* Reduce padding of the main block */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header with logo and centre name
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        logo_path = centro_config.get("logo_path", "")
        if logo_path:
            try:
                if logo_path.startswith("http"):
                    st.image(logo_path, width=120)
                elif os.path.exists(logo_path):
                    st.image(logo_path, width=120)
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

    # Initialize loading container (justo después del header)
    render_loading_container()

    # -----------------------------------------------------------------------
    # User Selector & Permissions Logic
    # -----------------------------------------------------------------------
    render_user_selector()
    
    available_tabs_labels = get_available_tabs()
    
    if not available_tabs_labels:
        st.error("⛔ Acceso denegado. No tienes permisos asignados para ver ninguna sección.")
        st.stop()

    # Main tabs
    tabs = st.tabs(available_tabs_labels)
    
    for i, tab_label in enumerate(available_tabs_labels):
        with tabs[i]:
            if "Admisión" in tab_label:
                from ui.admission_view import mostrar_admision
                mostrar_admision()
            elif "Triaje" in tab_label:
                ui.main_view.mostrar_asistente_triaje()
            elif "Atención Box" in tab_label:
                from ui.boxes_view import render_boxes_view
                render_boxes_view()
            elif "Consulta" in tab_label:
                from ui.admission_management_view import render_admission_management_view
                render_admission_management_view()
            elif "Auditoría" in tab_label and "v2" not in tab_label.lower():
                from ui.audit_panel.main_panel_v2 import mostrar_registro_auditoria_v2
                mostrar_registro_auditoria_v2()
            elif "Control de Salas" in tab_label:
                from ui.room_orchestrator import mostrar_orquestador_salas
                mostrar_orquestador_salas()
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
    # If disclaimer already accepted, show the main app
    mostrar_app_principal()