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

def get_image_base64(path: str) -> str | None:
    """
    Lee una imagen y la convierte a base64 para incrustar en HTML.
    
    Args:
        path (str): Ruta absoluta o relativa al archivo de imagen.
        
    Returns:
        str | None: String base64 codificado o None si falla.
    """
    import base64
    import os
    
    try:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except Exception:
        pass
    return None

def render_custom_download_button(data, filename, label="⬇️ Descargar", mime="application/pdf", key=None):
    """
    Renderiza un botón de descarga HTML personalizado usando base64.
    Esto fuerza al navegador a respetar el atributo 'download', evitando problemas de
    renombrado a UUID que ocurren con st.download_button en ciertos entornos.
    
    Args:
        data (bytes): Contenido del fichero en bytes.
        filename (str): Nombre del fichero (ej: 'informe.pdf').
        label (str): Texto del botón.
        mime (str): Tipo MIME.
        key (str): Clave única (no usada en HTML pero mantenida por compatibilidad de firma).
    """
    import base64
    import streamlit as st
    
    try:
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:{mime};base64,{b64}" download="{filename}" style="text-decoration:none;">'
        href += f'''
        <div style="
            display: inline-flex;
            -webkit-box-align: center;
            align-items: center;
            -webkit-box-pack: center;
            justify-content: center;
            font-weight: 400;
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            min-height: 38.4px;
            margin: 0px;
            line-height: 1.6;
            color: inherit;
            width: 100%;
            user-select: none;
            background-color: rgb(255, 255, 255);
            border: 1px solid rgba(49, 51, 63, 0.2);
            cursor: pointer;
            text-align: center;
            ">
            {label}
        </div>
        </a>
        '''
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error generando descarga: {e}")

