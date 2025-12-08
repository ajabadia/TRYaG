# path: src/utils/icons.py
# Creado: 2025-11-22
# Última modificación: 2025-11-22
"""
Módulo de utilidad para la gestión y renderizado de iconos SVG.
Permite cargar iconos desde la carpeta assets/icons y renderizarlos en Streamlit.
"""
import os
import streamlit as st

def get_icon_path(icon_name):
    """
    Devuelve la ruta absoluta de un icono dado su nombre (sin extensión).
    """
    # Asumiendo que assets está en la raíz del proyecto, dos niveles arriba de src/utils
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, 'src', 'assets', 'icons', f'{icon_name}.svg')

def load_icon(icon_name):
    """
    Lee el contenido de un archivo SVG y lo devuelve como string.
    """
    path = get_icon_path(icon_name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def render_icon(icon_name, size=24, color="currentColor", class_name=""):
    """
    Renderiza un icono SVG en Streamlit usando HTML.
    Permite ajustar tamaño y color (si el SVG usa currentColor).
    """
    svg_content = load_icon(icon_name)
    if svg_content:
        # Forzar que el SVG se adapte al contenedor ignorando sus dimensiones intrínsecas
        import re
        # Inyectar estilo directamente en la etiqueta svg
        svg_content = re.sub(r'<svg', '<svg style="width: 100%; height: 100%;"', svg_content, count=1)
        
        # Inyectar estilos básicos y envolver en un div con tamaño fijo
        st.markdown(
            f'<div class="{class_name}" style="display: inline-flex; align-items: center; justify-content: center; width: {size}px; height: {size}px; color: {color}; overflow: hidden;">{svg_content}</div>',
            unsafe_allow_html=True
        )
    else:
        st.warning(f"Icono no encontrado: {icon_name}")
