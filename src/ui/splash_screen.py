import streamlit as st
import time
import base64
import os
from ui.config.config_loader import load_centro_config

def get_image_base64(path):
    """Lee una imagen y la convierte a base64."""
    try:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except Exception:
        pass
    return None

def render_splash_screen():
    """
    Renderiza una pantalla de presentación con el logotipo animado.
    Simula la carga de componentes en segundo plano.
    """
    # CSS para la animación
    # Cargar CSS externo
    from utils.ui_utils import load_css
    load_css("src/assets/css/pages/splash.css")

    # Contenedor centrado
    with st.container():
        # 1. Cargar Logo TRYaGE (Título)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        tryag_path = os.path.join(root_dir, "src", "assets", "logos", "tryag.svg")
        
        tryag_src = ""
        if os.path.exists(tryag_path):
            b64 = get_image_base64(tryag_path)
            if b64:
                tryag_src = f"data:image/svg+xml;base64,{b64}"
        
        tryag_html = f'<img src="{tryag_src}" class="tryag-logo">' if tryag_src else '<h1 style="font-size: 4rem; color: #333;">TRYaGE</h1>'

        # 2. Cargar Logo Centro (Pulsing)
        config = load_centro_config()
        center_logo_path = config.get("logo_path", "")
        center_name = config.get("denominacion", "Centro Médico")
        
        center_src = "https://img.icons8.com/dusk/128/000000/hospital.png" # Fallback
        
        if center_logo_path:
            if center_logo_path.startswith("http"):
                center_src = center_logo_path
            else:
                # Lógica robusta de resolución de rutas (igual que en app.py)
                resolved_path = None
                
                # 1. Intentar ruta directa
                if os.path.exists(center_logo_path):
                    resolved_path = center_logo_path
                else:
                    # 2. Intentar relativa al root
                    abs_path = os.path.join(root_dir, center_logo_path)
                    if os.path.exists(abs_path):
                        resolved_path = abs_path
                    else:
                        # 3. Intentar corregir barras (Windows vs Linux)
                        fixed_path = center_logo_path.replace("\\", "/")
                        abs_path_fixed = os.path.join(root_dir, fixed_path)
                        if os.path.exists(abs_path_fixed):
                            resolved_path = abs_path_fixed
                
                if resolved_path:
                    b64 = get_image_base64(resolved_path)
                    if b64:
                        center_src = f"data:image/png;base64,{b64}"

        center_logo_html = f'<img src="{center_src}" class="center-logo">'
        
        st.markdown(
            f"""
            <div class="splash-container">
                {tryag_html}
                {center_logo_html}
                <div class="center-name">{center_name}</div>
                <div class="loading-bar">
                    <div class="loading-progress"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Simular carga
    time.sleep(4.0)
