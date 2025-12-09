import streamlit as st
from datetime import date
import os
from utils.icons import render_icon

def render_footer(centro_config):
    """
    Renderiza el pie de página con los datos del centro y el branding de TRY-a-G.
    
    Args:
        centro_config (dict): Configuración del centro (denominación, cif, etc.)
    """
    st.divider()
    
    # 1. Datos del Centro
    with st.container():
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            denominacion = centro_config.get("denominacion", "")
            cif = centro_config.get("cif", "")
            if denominacion:
                st.caption(f"**{denominacion}**")
            if cif:
                st.caption(f"CIF: {cif}")
        with col_f2:
            email = centro_config.get("email", "")
            telefono = centro_config.get("telefono", "")
            if email:
                ic, txt = st.columns([0.1, 10])
                with ic:
                    render_icon("email", size=12)
                with txt:
                    st.caption(email)
            if telefono:
                ic, txt = st.columns([0.1, 10])
                with ic:
                    render_icon("phone", size=12)
                with txt:
                    st.caption(telefono)
        with col_f3:
            direccion = centro_config.get("direccion", "")
            if direccion:
                ic, txt = st.columns([0.1, 10])
                with ic:
                    render_icon("location", size=12)
                with txt:
                    st.caption(direccion)

    # 2. Branding TRY-a-G
    st.markdown("---")
    
    # Contenedor flex para Logo y Texto en una sola línea
    # Ruta relativa desde la raíz de ejecución
    logo_path = os.path.join("src", "assets", "logos", "tryag.svg")
    from utils.ui_utils import get_image_base64
    
    logo_html = ""
    if os.path.exists(logo_path):
        b64_logo = get_image_base64(logo_path)
        if b64_logo:
             logo_html = f'<img src="data:image/svg+xml;base64,{b64_logo}" style="height: 40px; w: auto; margin-right: 15px;">'
        else:
             logo_html = "<strong>TRY-a-G</strong> "
    else:
         logo_html = "<strong>TRY-a-G</strong> "

    version = "v0.1 beta"
    fecha = date.today().strftime("%d/%m/%Y")
    
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: row; align-items: center; justify-content: center; width: 100%; margin-top: 10px; color: gray;">
            {logo_html}
            <span style="font-size: 0.9em; border-left: 1px solid #ccc; padding-left: 15px;">
                Asistente de Triaje Inteligente &copy; {date.today().year} | {version} ({fecha})
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
