import streamlit as st
import streamlit.components.v1 as components
import os
import base64
from utils.file_utils import get_file_base64
from utils.image_utils import get_or_create_thumbnail_base64

# Intentamos importar el decorador experimental de diálogo
try:
    from streamlit import dialog as dialog_decorator
except ImportError:
    dialog_decorator = None

def _render_image_viewer(file_path: str, file_ext: str):
    """
    Renderiza el visor de imágenes con controles de zoom, rotación y filtros.
    """
    # Obtener base64 de la imagen
    b64_img = get_file_base64(file_path)
    if not b64_img:
        st.error(f"No se pudo cargar la imagen: {file_path}")
        return

    # Determinar tipo MIME
    mime_type = f"image/{file_ext}"
    if file_ext == 'jpg': mime_type = 'image/jpeg'
    
    icons = {
        "zoom_in": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>',
        "zoom_out": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>',
        "fit": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>',
        "rotate_left": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>',
        "rotate_right": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 12a9 9 0 1 1-9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path></svg>',
        "invert": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a10 10 0 0 1 0 20z" fill="currentColor"></path></svg>',
        "brightness_up": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>',
        "contrast": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><path d="M12 2v20"></path></svg>',
        "reset": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M12 7v5l3 3"></path></svg>',
        "download": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'
    }

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {{ margin: 0; padding: 0; height: 100%; overflow: hidden; background-color: #000; font-family: sans-serif; }}
            .viewer-container {{ display: flex; width: 100%; height: 100vh; }}
            
            /* Barras Laterales */
            .toolbar {{
                width: 50px;
                background-color: #1a1a1a;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 10px 0;
                gap: 10px;
                z-index: 10;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }}
            .toolbar-right {{ border-left: 1px solid #333; }}
            .toolbar-left {{ border-right: 1px solid #333; }}
            
            /* Botones */
            .btn {{
                width: 36px;
                height: 36px;
                background: transparent;
                border: none;
                color: #ccc;
                cursor: pointer;
                border-radius: 5px;
                display: flex;
                justify-content: center;
                align-items: center;
                transition: all 0.2s;
                text-decoration: none; /* Para el enlace de descarga */
            }}
            .btn:hover {{ background-color: #333; color: #fff; }}
            .btn:active {{ transform: scale(0.95); }}
            .btn.active {{ color: #4CAF50; }}
            
            /* Área Principal */
            .viewport {{
                flex-grow: 1;
                position: relative;
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
                background-image: radial-gradient(#222 1px, transparent 1px);
                background-size: 20px 20px;
                cursor: grab;
            }}
            .viewport:active {{ cursor: grabbing; }}
            
            /* Imagen */
            #target-img {{
                max-width: 95%; /* Margen de seguridad */
                max-height: 95%;
                transition: transform 0.1s ease-out, filter 0.2s ease;
                transform-origin: center;
                user-select: none;
                pointer-events: none; /* Para que el arrastre sea en el viewport */
            }}
            
            /* Tooltip simple */
            .btn[title]:hover::after {{
                content: attr(title);
                position: absolute;
                left: 60px;
                background: #333;
                color: #fff;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 20;
            }}
            .toolbar-right .btn[title]:hover::after {{
                left: auto;
                right: 60px;
            }}
            
            /* Info Overlay */
            .info-overlay {{
                position: absolute;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0,0,0,0.7);
                color: #fff;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            .info-overlay.visible {{ opacity: 1; }}

        </style>
    </head>
    <body>
        <div class="viewer-container">
            <!-- Barra Izquierda: Navegación -->
            <div class="toolbar toolbar-left">
                <button class="btn" onclick="zoomIn()" title="Zoom In (+)">{icons['zoom_in']}</button>
                <button class="btn" onclick="zoomOut()" title="Zoom Out (-)">{icons['zoom_out']}</button>
                <button class="btn" onclick="fitToScreen()" title="Ajustar a Pantalla">{icons['fit']}</button>
                <div style="flex-grow: 1;"></div> <!-- Espaciador -->
                <a class="btn" href="data:{mime_type};base64,{b64_img}" download="{os.path.basename(file_path)}" title="Descargar Imagen">
                    {icons['download']}
                </a>
                <button class="btn" onclick="resetAll()" title="Restablecer Todo" style="color: #ff6b6b;">{icons['reset']}</button>
            </div>

            <!-- Área Central -->
            <div class="viewport" id="viewport">
                <img id="target-img" src="data:{mime_type};base64,{b64_img}">
                <div id="info-overlay" class="info-overlay">Zoom: 100%</div>
            </div>

            <!-- Barra Derecha: Manipulación -->
            <div class="toolbar toolbar-right">
                <button class="btn" onclick="rotate(-90)" title="Rotar Izquierda">{icons['rotate_left']}</button>
                <button class="btn" onclick="rotate(90)" title="Rotar Derecha">{icons['rotate_right']}</button>
                <div style="height: 1px; background: #333; width: 80%;"></div>
                <button class="btn" onclick="toggleInvert()" title="Invertir Colores (Negativo)" id="btn-invert">{icons['invert']}</button>
                <button class="btn" onclick="adjustBrightness(10)" title="Más Brillo">{icons['brightness_up']}</button>
                <button class="btn" onclick="adjustBrightness(-10)" title="Menos Brillo" style="opacity: 0.7;">{icons['brightness_up']}</button>
                <button class="btn" onclick="adjustContrast(10)" title="Más Contraste">{icons['contrast']}</button>
                <button class="btn" onclick="adjustContrast(-10)" title="Menos Contraste" style="opacity: 0.7;">{icons['contrast']}</button>
            </div>
        </div>

        <script>
            const img = document.getElementById('target-img');
            const viewport = document.getElementById('viewport');
            const overlay = document.getElementById('info-overlay');
            
            // Estado
            let state = {{
                scale: 1,
                pX: 0,
                pY: 0,
                rotation: 0,
                invert: 0,
                brightness: 100,
                contrast: 100
            }};

            // Configuración
            const ZOOM_SPEED = 0.1;
            const MAX_ZOOM = 5;
            const MIN_ZOOM = 0.1;

            function updateTransform() {{
                img.style.transform = `translate(${{state.pX}}px, ${{state.pY}}px) scale(${{state.scale}}) rotate(${{state.rotation}}deg)`;
                showOverlay(`Zoom: ${{Math.round(state.scale * 100)}}%`);
            }}

            function updateFilters() {{
                img.style.filter = `invert(${{state.invert}}) brightness(${{state.brightness}}%) contrast(${{state.contrast}}%)`;
            }}

            function showOverlay(text) {{
                overlay.innerText = text;
                overlay.classList.add('visible');
                clearTimeout(window.overlayTimer);
                window.overlayTimer = setTimeout(() => overlay.classList.remove('visible'), 1500);
            }}

            // --- Funciones de Control ---

            window.zoomIn = () => {{
                state.scale *= 1.2;
                if(state.scale > MAX_ZOOM) state.scale = MAX_ZOOM;
                updateTransform();
            }};

            window.zoomOut = () => {{
                state.scale /= 1.2;
                if(state.scale < MIN_ZOOM) state.scale = MIN_ZOOM;
                updateTransform();
            }};

            window.fitToScreen = () => {{
                state.scale = 1;
                state.pX = 0;
                state.pY = 0;
                // state.rotation = 0; // Opcional: resetear rotación al ajustar
                updateTransform();
            }};

            window.rotate = (deg) => {{
                state.rotation = (state.rotation + deg) % 360;
                updateTransform();
            }};

            window.toggleInvert = () => {{
                state.invert = state.invert === 0 ? 1 : 0;
                document.getElementById('btn-invert').classList.toggle('active');
                updateFilters();
                showOverlay(state.invert ? "Modo Negativo: ON" : "Modo Negativo: OFF");
            }};

            window.adjustBrightness = (delta) => {{
                state.brightness += delta;
                if(state.brightness < 0) state.brightness = 0;
                updateFilters();
                showOverlay(`Brillo: ${{state.brightness}}%`);
            }};

            window.adjustContrast = (delta) => {{
                state.contrast += delta;
                if(state.contrast < 0) state.contrast = 0;
                updateFilters();
                showOverlay(`Contraste: ${{state.contrast}}%`);
            }};

            window.resetAll = () => {{
                state = {{ scale: 1, pX: 0, pY: 0, rotation: 0, invert: 0, brightness: 100, contrast: 100 }};
                document.getElementById('btn-invert').classList.remove('active');
                updateTransform();
                updateFilters();
                showOverlay("Restablecido");
            }};

            // --- Eventos de Ratón (Pan & Zoom) ---

            let isDragging = false;
            let startX, startY;

            viewport.onmousedown = (e) => {{
                e.preventDefault();
                isDragging = true;
                startX = e.clientX - state.pX;
                startY = e.clientY - state.pY;
                viewport.style.cursor = 'grabbing';
            }};

            window.onmouseup = () => {{
                isDragging = false;
                viewport.style.cursor = 'grab';
            }};

            window.onmousemove = (e) => {{
                if (!isDragging) return;
                e.preventDefault();
                state.pX = e.clientX - startX;
                state.pY = e.clientY - startY;
                updateTransform();
            }};

            viewport.onwheel = (e) => {{
                e.preventDefault();
                const delta = -Math.sign(e.deltaY);
                const factor = 1.1;
                
                if (delta > 0) {{
                    state.scale *= factor;
                }} else {{
                    state.scale /= factor;
                }}
                
                // Limites
                if(state.scale > MAX_ZOOM) state.scale = MAX_ZOOM;
                if(state.scale < MIN_ZOOM) state.scale = MIN_ZOOM;

                updateTransform();
            }};

        </script>
    </body>
    </html>
    """
    # Altura ajustada para ocupar casi toda la pantalla disponible en el diálogo (450px)
    components.html(html_code, height=450, scrolling=False)

def _render_pdf_viewer(file_path: str):
    """Renderiza el visor de PDF."""
    b64_pdf = get_file_base64(file_path)
    if not b64_pdf:
        st.error("No se pudo cargar el PDF.")
        return
        
    pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def render_media_content(file_path: str, file_ext: str):
    """
    Renderiza el contenido del archivo según su extensión.
    """
    if not os.path.exists(file_path):
        st.error(f"El archivo no existe: {file_path}")
        return

    if file_ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
        _render_image_viewer(file_path, file_ext)
    elif file_ext in ['mp3', 'wav', 'ogg']:
        st.audio(file_path, format=f'audio/{file_ext}')
    elif file_ext in ['mp4', 'webm']:
        st.video(file_path, format=f'video/{file_ext}')
    elif file_ext == 'pdf':
        _render_pdf_viewer(file_path)
    else:
        st.warning(f"Visualización no soportada para archivos .{file_ext}")

def render_clickable_thumbnail(file_path: str, file_name: str, file_ext: str, key: str, on_click=None, args=()):
    """
    Renderiza una miniatura que actúa como un botón clicable con efecto hover.
    Usa un hack CSS para superponer un botón transparente.
    """
    # Generar miniatura
    thumb_b64 = None
    if file_ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
        thumb_b64 = get_or_create_thumbnail_base64(file_path, key, size=(200, 200)) # Usar key como hash temporal si no hay md5
    
    # CSS para el contenedor y el efecto hover
    st.markdown(f"""
    <style>
        .thumb-container-{key} {{
            position: relative;
            width: 100%;
            aspect-ratio: 1;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s ease;
            border: 1px solid #eee;
        }}
        .thumb-container-{key}:hover {{
            transform: scale(0.95);
            border-color: #aaa;
        }}
        .thumb-img-{key} {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .thumb-overlay-btn-{key} {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10;
            opacity: 0; /* Transparente */
            cursor: pointer;
        }}
        /* Ajuste para el botón de Streamlit para que ocupe todo el contenedor */
        .thumb-wrapper-{key} button {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100% !important;
            height: 100% !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Layout
    container = st.container()
    with container:
        # Contenedor visual (Imagen)
        if thumb_b64:
            img_html = f'<div class="thumb-container-{key}"><img src="{thumb_b64}" class="thumb-img-{key}"></div>'
        else:
            img_html = f'<div class="thumb-container-{key}" style="display:flex;align-items:center;justify-content:center;background:#f0f0f0;font-weight:bold;color:#888;">{file_ext.upper()}</div>'
        
        st.markdown(img_html, unsafe_allow_html=True)
        
        # Botón invisible superpuesto (usando columnas para posicionamiento relativo si fuera necesario, 
        # pero aquí usamos el hack de CSS sobre el botón generado por Streamlit)
        # Nota: Streamlit no permite poner botones DENTRO de HTML arbitrario fácilmente.
        # Solución: Renderizamos el botón justo debajo con margen negativo para subirlo, 
        # o usamos un botón normal y confiamos en el usuario.
        # Dado las limitaciones, usaremos un botón normal de Streamlit con etiqueta "Ver" si el hack es inestable,
        # pero intentaremos el hack de "botón invisible que cubre el área".
        
        # Simplificación para robustez: Botón "Ver" debajo, pero estilizado.
        # O mejor: Usar st.button normal pero con la imagen como label (no soportado nativamente con imagen).
        
        # Enfoque robusto: Botón transparente que ocupa el espacio.
        # Requiere que el botón se renderice ANTES o DESPUES y se mueva con CSS.
        # Vamos a usar un botón normal de Streamlit que dice "👁️ Ver" pero con estilo minimalista.
        # Enfoque robusto: Botón normal de Streamlit con icono
        if st.button("Ver", key=key, on_click=on_click, args=args, use_container_width=True, icon=":material/visibility:"):
            pass


# Definimos la función del diálogo si el decorador está disponible
if dialog_decorator:
    @dialog_decorator("Visualizar Archivo", width="large")
    def show_media_dialog(files_list: list, start_index: int):
        """
        Muestra el contenido multimedia en un diálogo modal con carrusel.
        files_list: Lista de dicts {'path': str, 'name': str, 'ext': str, 'md5': str}
        """
        if 'viewer_active_index' not in st.session_state:
            st.session_state.viewer_active_index = start_index
        
        # Asegurar índice válido
        if st.session_state.viewer_active_index < 0 or st.session_state.viewer_active_index >= len(files_list):
            st.session_state.viewer_active_index = 0

        current_file = files_list[st.session_state.viewer_active_index]
        
        # --- 1. Visor Principal ---
        render_media_content(current_file['path'], current_file['ext'])
        st.caption(f"{current_file['name']} ({st.session_state.viewer_active_index + 1}/{len(files_list)})")

        # --- 2. Carrusel de Miniaturas (si hay más de 1 archivo) ---
        if len(files_list) > 1:
            st.divider()
            
            # Configuración del carrusel
            ITEMS_PER_PAGE = 6
            total_pages = (len(files_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            
            if 'carousel_page' not in st.session_state:
                st.session_state.carousel_page = st.session_state.viewer_active_index // ITEMS_PER_PAGE

            # Controles de Paginación
            col_prev, col_thumbs, col_next = st.columns([1, 10, 1])
            
            with col_prev:
                if st.button("Anterior", key="car_prev", disabled=st.session_state.carousel_page == 0, icon=":material/arrow_back:"):
                    st.session_state.carousel_page -= 1
            
            with col_next:
                if st.button("Siguiente", key="car_next", disabled=st.session_state.carousel_page >= total_pages - 1, icon=":material/arrow_forward:"):
                    st.session_state.carousel_page += 1

            # Renderizar Miniaturas
            start_idx = st.session_state.carousel_page * ITEMS_PER_PAGE
            end_idx = min(start_idx + ITEMS_PER_PAGE, len(files_list))
            page_items = files_list[start_idx:end_idx]
            
            with col_thumbs:
                cols = st.columns(ITEMS_PER_PAGE)
                for i, item in enumerate(page_items):
                    real_idx = start_idx + i
                    with cols[i]:
                        is_active = (real_idx == st.session_state.viewer_active_index)
                        
                        # Estilo para indicar activo
                        border_color = "#4CAF50" if is_active else "#ddd"
                        border_width = "3px" if is_active else "1px"
                        
                        # Miniatura
                        thumb = get_or_create_thumbnail_base64(item['path'], item.get('md5', str(real_idx)), size=(100, 100))
                        
                        if thumb:
                            st.markdown(f"""
                            <div style="border: {border_width} solid {border_color}; border-radius: 5px; overflow: hidden; height: 60px; display: flex; justify-content: center; align-items: center; background: #333;">
                                <img src="{thumb}" style="max-width: 100%; max-height: 100%; object-fit: cover;">
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="border: {border_width} solid {border_color}; border-radius: 5px; height: 60px; display: flex; justify-content: center; align-items: center; background: #eee; font-size: 10px;">
                                {item['ext'].upper()}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Botón de selección
                        if st.button("Ver", key=f"sel_{real_idx}", use_container_width=True, icon=":material/visibility:"):
                            st.session_state.viewer_active_index = real_idx


def open_media_viewer(files_list: list, start_index: int = 0, key: str = None):
    """
    Punto de entrada principal para abrir el visor multi-archivo.
    files_list: Lista de dicts {'path', 'name', 'ext', 'md5'}
    """
    if dialog_decorator:
        # Inicializamos el estado antes de abrir
        if st.button("Ver Archivos", key=key, use_container_width=True, icon=":material/visibility:"):
            st.session_state.viewer_active_index = start_index
            st.session_state.carousel_page = start_index // 6 # Sincronizar página
            show_media_dialog(files_list, start_index)
    else:
        # Fallback a Popover (Simplificado, solo muestra el seleccionado)
        with st.popover("Visualizar", use_container_width=True, icon=":material/visibility:"):
            file = files_list[start_index]
            if file['ext'] in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                st.image(file['path'], caption=file['name'], use_container_width=True)
            else:
                render_media_content(file['path'], file['ext'])
