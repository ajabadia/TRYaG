import streamlit as st
import time
import base64
import os
from ui.config_panel import load_centro_config

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
    st.markdown(
        """
        <style>
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.9; }
            50% { transform: scale(1.05); opacity: 1; }
            100% { transform: scale(1); opacity: 0.9; }
        }
        
        @keyframes fadeOut {
            0% { opacity: 1; }
            100% { opacity: 0; }
        }

        .splash-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh;
            animation: fadeOut 0.5s ease-in-out 3.5s forwards;
        }
        
        /* Logo TRYaGE (Título) */
        .tryag-logo {
            width: 300px;
            margin-bottom: 40px;
            object-fit: contain;
        }

        /* Logo Centro (Pulsing) */
        .center-logo {
            width: 150px;
            height: 150px;
            object-fit: contain;
            animation: pulse 2s infinite ease-in-out;
            margin-bottom: 20px;
            border-radius: 50%; /* Opcional: si el logo es cuadrado, lo hace redondo */
            padding: 10px;
            background: rgba(255, 255, 255, 0.5);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .center-name {
            font-family: 'Helvetica Neue', sans-serif;
            font-size: 1.5rem;
            font-weight: 400;
            color: #555;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .loading-bar {
            width: 250px;
            height: 4px;
            background-color: #f0f0f0;
            border-radius: 2px;
            margin-top: 30px;
            overflow: hidden;
        }
        
        .loading-progress {
            width: 100%;
            height: 100%;
            background-color: #28a745;
            transform-origin: left;
            animation: progress 3.5s ease-in-out forwards;
        }
        
        @keyframes progress {
            0% { transform: scaleX(0); }
            100% { transform: scaleX(1); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Contenedor centrado
    with st.container():
        # 1. Cargar Logo TRYaGE (Título)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        tryag_path = os.path.join(root_dir, "assets", "logos", "tryag.svg")
        
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
                if os.path.exists(center_logo_path):
                    b64 = get_image_base64(center_logo_path)
                    if b64:
                        center_src = f"data:image/png;base64,{b64}"
                else:
                    # Intentar ruta relativa al root
                    abs_path = os.path.join(root_dir, center_logo_path)
                    if os.path.exists(abs_path):
                        b64 = get_image_base64(abs_path)
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
