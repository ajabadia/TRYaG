# path: src/ui/loading_indicator.py
# Creado: 2025-11-25
# Actualizado: 2025-11-25 - Añadidas animaciones suaves y delay
"""
Componente centralizado para mostrar indicadores de carga durante operaciones de base de datos.
Proporciona feedback visual al usuario cuando se están recuperando datos, con animaciones suaves
para evitar parpadeos en operaciones rápidas.
"""

import streamlit as st
from contextlib import contextmanager
from typing import Optional
import time
import threading

# Clave para el contenedor de estado global
LOADING_CONTAINER_KEY = "_global_loading_container"
LOADING_STATE_KEY = "_global_loading_state"

# Configuración de tiempos (en segundos)
SHOW_DELAY = 0.5  # Esperar 500ms antes de mostrar el indicador
MIN_DISPLAY_TIME = 1.0  # Tiempo mínimo que debe estar visible si se muestra
FADE_DURATION = 0.3  # Duración de las animaciones fade in/out


def init_loading_container():
    """
    Inicializa el contenedor global de loading en la parte superior de la página.
    Debe llamarse una vez al inicio de cada página, justo después del header.
    """
    if LOADING_CONTAINER_KEY not in st.session_state:
        st.session_state[LOADING_CONTAINER_KEY] = st.empty()
    
    if LOADING_STATE_KEY not in st.session_state:
        st.session_state[LOADING_STATE_KEY] = {
            "is_loading": False,
            "message": "",
            "show_time": None,
        }
    
    return st.session_state[LOADING_CONTAINER_KEY]


def _get_loading_css():
    """Retorna el CSS para las animaciones de fade in/out."""
    return f"""
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeOut {{
        from {{ opacity: 1; transform: translateY(0); }}
        to {{ opacity: 0; transform: translateY(-10px); }}
    }}
    .loading-indicator {{
        animation: fadeIn {FADE_DURATION}s ease-in;
    }}
    .loading-indicator-out {{
        animation: fadeOut {FADE_DURATION}s ease-out;
    }}
    </style>
    """


def show_loading(message: str = "Recuperando datos..."):
    """
    Muestra el indicador de carga con un mensaje personalizado.
    
    Args:
        message: Mensaje a mostrar durante la carga
    """
    if LOADING_CONTAINER_KEY in st.session_state:
        container = st.session_state[LOADING_CONTAINER_KEY]
        st.session_state[LOADING_STATE_KEY]["is_loading"] = True
        st.session_state[LOADING_STATE_KEY]["message"] = message
        st.session_state[LOADING_STATE_KEY]["show_time"] = time.time()
        
        with container:
            # Inyectar CSS para animaciones
            st.markdown(_get_loading_css(), unsafe_allow_html=True)
            
            # Mostrar indicador con animación
            st.markdown(
                f"""
                <div class="loading-indicator">
                """,
                unsafe_allow_html=True
            )
            st.info(f":material/sync: {message}", icon="ℹ️")
            st.markdown("</div>", unsafe_allow_html=True)


def hide_loading():
    """
    Oculta el indicador de carga, respetando el tiempo mínimo de visualización.
    """
    if LOADING_CONTAINER_KEY in st.session_state:
        state = st.session_state[LOADING_STATE_KEY]
        
        # Si se mostró el indicador, asegurar que esté visible el tiempo mínimo
        if state["show_time"] is not None:
            elapsed = time.time() - state["show_time"]
            if elapsed < MIN_DISPLAY_TIME:
                # Esperar el tiempo restante
                time.sleep(MIN_DISPLAY_TIME - elapsed)
        
        # Limpiar el contenedor
        container = st.session_state[LOADING_CONTAINER_KEY]
        container.empty()
        
        # Resetear estado
        st.session_state[LOADING_STATE_KEY]["is_loading"] = False
        st.session_state[LOADING_STATE_KEY]["message"] = ""
        st.session_state[LOADING_STATE_KEY]["show_time"] = None


@contextmanager
def loading_data(message: str = "Recuperando datos de la base de datos..."):
    """
    Context manager para mostrar indicador de carga durante operaciones de BD.
    
    Implementa un delay antes de mostrar el indicador para evitar parpadeos en
    operaciones rápidas. Si la operación termina antes del delay, no se muestra nada.
    
    Uso:
        with loading_data("Cargando registros de auditoría..."):
            datos = repositorio.get_recent(limit=1000)
    
    Args:
        message: Mensaje a mostrar durante la carga
    """
    start_time = time.time()
    should_show = [True]  # Lista mutable para compartir entre threads
    indicator_shown = [False]
    
    def delayed_show():
        """Muestra el indicador después del delay si la operación sigue en curso."""
        time.sleep(SHOW_DELAY)
        if should_show[0]:
            show_loading(message)
            indicator_shown[0] = True
    
    # Iniciar thread para mostrar el indicador con delay
    from streamlit.runtime.scriptrunner import add_script_run_ctx
    show_thread = threading.Thread(target=delayed_show, daemon=True)
    add_script_run_ctx(show_thread)
    show_thread.start()
    
    try:
        yield
    finally:
        # Marcar que la operación terminó
        should_show[0] = False
        
        # Esperar a que el thread termine
        show_thread.join(timeout=SHOW_DELAY + 0.1)
        
        # Si se mostró el indicador, ocultarlo
        if indicator_shown[0]:
            hide_loading()


def render_loading_container():
    """
    Renderiza el contenedor de loading en la interfaz.
    Debe llamarse en el layout principal, justo después del header.
    
    Returns:
        El contenedor donde se mostrarán los mensajes de carga
    """
    # Crear un contenedor fijo en la parte superior
    loading_container = st.container()
    
    # Guardar referencia en session_state
    st.session_state[LOADING_CONTAINER_KEY] = loading_container.empty()
    
    if LOADING_STATE_KEY not in st.session_state:
        st.session_state[LOADING_STATE_KEY] = {
            "is_loading": False,
            "message": "",
            "show_time": None,
        }
    
    return st.session_state[LOADING_CONTAINER_KEY]
