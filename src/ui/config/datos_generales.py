# path: src/ui/config/datos_generales.py
# Creado: 2025-11-25
"""
UI para configuración de datos generales del centro.
Componente modular para la sección de información básica.
"""
import streamlit as st
from db.repositories.centros import get_centros_repository


def render_datos_generales():
    """
    Renderiza formulario de datos generales del centro.
    Incluye: denominación, CIF, dirección, contacto, logo y mensaje.
    """
    st.markdown("### 🏥 Datos Generales del Centro")
    st.markdown("Información básica y datos de contacto del centro médico.")
    
    # Cargar configuración actual
    try:
        centros_repo = get_centros_repository()
        centro = centros_repo.get_centro_principal()
        if not centro:
            centro = {}
    except Exception as e:
        st.error(f"Error al cargar configuración: {e}")
        centro = {}
    
    with st.container(border=True):
        # Identificación
        st.markdown("#### 📋 Identificación")
        col1, col2 = st.columns(2)
        
        with col1:
            codigo_centro = st.text_input(
                "Código del Centro",
                value=centro.get('codigo', ''),
                help="Código único identificador del centro",
                placeholder="Ej: CTR001"
            )
        
        with col2:
            cif = st.text_input(
                "CIF/NIF",
                value=centro.get('cif', ''),
                help="CIF o NIF del centro",
                placeholder="Ej: A12345678"
            )
        
        denominacion = st.text_input(
            "Denominación del Centro",
            value=centro.get('denominacion', ''),
            help="Nombre oficial completo del centro médico",
            placeholder="Ej: Centro Médico Santa María"
        )
        
        st.markdown("---")
        
        # Contacto
        st.markdown("#### 📞 Datos de Contacto")
        col3, col4 = st.columns(2)
        
        with col3:
            telefono = st.text_input(
                "Teléfono",
                value=centro.get('telefono', ''),
                help="Teléfono principal del centro",
                placeholder="Ej: +34 912 345 678"
            )
        
        with col4:
            email = st.text_input(
                "Email",
                value=centro.get('email', ''),
                help="Correo electrónico de contacto",
                placeholder="Ej: info@centro.com"
            )
        
        direccion = st.text_area(
            "Dirección",
            value=centro.get('direccion', ''),
            help="Dirección completa del centro",
            placeholder="Calle, número, código postal, ciudad",
            height=80
        )
        
        st.markdown("---")
        
        # Personalización
        st.markdown("#### 🎨 Personalización")
        logo_path = st.text_input(
            "Logo del Centro (URL o ruta)",
            value=centro.get('logo_path', ''),
            help="URL del logo o ruta local al archivo de imagen",
            placeholder="https://ejemplo.com/logo.png o /assets/logo.png"
        )
        
        # Vista previa del logo
        if logo_path:
            try:
                col_preview1, col_preview2 = st.columns([1, 3])
                with col_preview1:
                    if logo_path.startswith('http'):
                        st.image(logo_path, width=100, caption="Vista previa")
                    else:
                        st.caption("💡 Vista previa disponible solo para URLs")
            except Exception:
                st.caption("⚠️ No se pudo cargar la vista previa")
        
        mensaje_centro = st.text_area(
            "Mensaje del Header",
            value=centro.get('mensaje', ''),
            help="Mensaje que aparece en el encabezado de la aplicación",
            placeholder="Ej: Atención médica de calidad - Disponible 24/7",
            height=60
        )
        
        st.markdown("---")
        
        # Botones de acción
        col_save, col_reset = st.columns(2)
        
        with col_save:
            if st.button(
                "💾 Guardar Configuración",
                type="primary",
                use_container_width=True,
                help="Guarda todos los cambios realizados"
            ):
                try:
                    config_to_save = {
                        'codigo': codigo_centro,
                        'denominacion': denominacion,
                        'cif': cif,
                        'direccion': direccion,
                        'email': email,
                        'telefono': telefono,
                        'logo_path': logo_path,
                        'mensaje': mensaje_centro,
                        'salas': centro.get('salas', [])  # Mantener salas existentes
                    }
                    
                    centros_repo.create_or_update_centro(
                        codigo=config_to_save['codigo'],
                        denominacion=config_to_save['denominacion'],
                        cif=config_to_save.get('cif'),
                        direccion=config_to_save.get('direccion'),
                        email=config_to_save.get('email'),
                        telefono=config_to_save.get('telefono'),
                        logo_path=config_to_save.get('logo_path'),
                        mensaje=config_to_save.get('mensaje'),
                        salas=config_to_save.get('salas', []),
                        updated_by="admin"
                    )
                    
                    st.success("✅ Configuración guardada correctamente")
                    
                    # Invalidar caché de sesión para forzar recarga
                    if 'centro_config' in st.session_state:
                        del st.session_state.centro_config
                        
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")
        
        with col_reset:
            if st.button(
                "🔄 Restablecer Valores",
                use_container_width=True,
                help="Vuelve a cargar los valores guardados en la base de datos"
            ):
                st.rerun()

    st.markdown('<div class="debug-footer">src/ui/config/datos_generales.py</div>', unsafe_allow_html=True)
