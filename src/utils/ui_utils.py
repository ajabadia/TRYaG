# path: src/utils/ui_utils.py
"""
Utilidades compartidas para la interfaz de usuario.
Centraliza lógica de estilos, colores y formateo visual.
"""

# Colores por tipo de sala
ROOM_TYPE_COLORS = {
    "admision": "#28a745",   # Verde
    "triaje": "#17a2b8",     # Cyan/Azul claro
    "box": "#ffc107",        # Amarillo
    "consulta": "#6c757d",   # Gris
    "default": "#6c757d"     # Gris por defecto
}

def get_room_color(room_type: str) -> str:
    """
    Devuelve el código de color hexadecimal asociado a un tipo de sala.
    
    Args:
        room_type (str): El tipo de sala (ej: 'admision', 'triaje', 'box').
        
    Returns:
        str: Código de color hexadecimal.
    """
    if not room_type:
        return ROOM_TYPE_COLORS["default"]
        
    return ROOM_TYPE_COLORS.get(room_type.lower(), ROOM_TYPE_COLORS["default"])

def load_css(file_path: str):
    """
    Carga un archivo CSS y lo inyecta en la aplicación Streamlit.
    
    Args:
        file_path (str): Ruta relativa al archivo CSS desde la raíz del proyecto.
    """
    import streamlit as st
    import os
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Archivo CSS no encontrado: {file_path}")
