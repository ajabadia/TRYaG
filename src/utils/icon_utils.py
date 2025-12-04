# path: src/utils/icon_utils.py
# Creado: 2025-11-22
"""
Utilidades para cargar y renderizar iconos SVG.
"""
import os
import base64

def load_svg_icon(icon_name: str, size: int = 24, color: str = "currentColor") -> str:
    """
    Carga un icono SVG desde assets/icons y lo retorna como HTML inline.
    
    Args:
        icon_name: Nombre del archivo SVG sin extensión
        size: Tamaño del icono en píxeles
        color: Color del icono (CSS color o 'currentColor')
    
    Returns:
        HTML string con el SVG inline
    """
    icon_path = os.path.join('src', 'assets', 'icons', f'{icon_name}.svg')
    
    if not os.path.exists(icon_path):
        return f"[{icon_name}]"  # Fallback si no existe
    
    try:
        with open(icon_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Inyectar tamaño y color
        svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')
        svg_content = svg_content.replace('<svg', f'<svg width="{size}" height="{size}"', 1)
        
        return svg_content
    except Exception:
        return f"[{icon_name}]"

def get_icon_html(icon_name: str, size: int = 20) -> str:
    """
    Retorna HTML para mostrar un icono inline en markdown.
    
    Args:
        icon_name: Nombre del icono SVG
        size: Tamaño en píxeles
    
    Returns:
        HTML string listo para usar en st.markdown con unsafe_allow_html=True
    """
    svg = load_svg_icon(icon_name, size)
    return f'<span style="display:inline-block; vertical-align:middle; margin-right:8px;">{svg}</span>'
