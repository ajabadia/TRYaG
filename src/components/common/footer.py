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
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    
    with col_b2:
        # Contenedor centrado para el logo y la versión
        st.markdown(
            """
            <div style="display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 15px;">
            """,
            unsafe_allow_html=True
        )
        
        # Logo
        # Ruta relativa desde la raíz de ejecución (donde se corre streamlit run src/app.py)
        # Asumiendo que se corre desde 'web/'
        logo_path = os.path.join("assets", "logos", "tryag.svg")
        
        if os.path.exists(logo_path):
            st.image(logo_path, width=80)
        else:
            # Fallback si no encuentra el svg
            st.markdown("### TRY-a-G")

        # Versión y Fecha
        version = "v0.1 beta"
        fecha = date.today().strftime("%d/%m/%Y")
        
        st.markdown(f"<span style='color: gray; font-size: 0.8em;'>{version} | {fecha}</span>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
