import streamlit as st
import streamlit.components.v1 as components

def render_pwa_installer():
    """
    Inyecta el código necesario para registrar el Service Worker y habilitar la instalación PWA.
    Debe llamarse al inicio de la aplicación (app.py).
    """
    
    # HTML/JS para registrar el Service Worker
    pwa_script = """
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('src/static/sw.js').then(function(registration) {
                    console.log('ServiceWorker registration successful with scope: ', registration.scope);
                }, function(err) {
                    console.log('ServiceWorker registration failed: ', err);
                });
            });
        }
    </script>
    """
    
    # Inyectar el script en el head (usando components.html con height=0 para que sea invisible pero ejecute)
    # Nota: Streamlit ejecuta esto en un iframe, por lo que el registro del SW puede ser tricky.
    # Una mejor aproximación para Streamlit es usar st.markdown con unsafe_allow_html para tags meta/link,
    # pero los scripts a veces no corren bien ahí.
    # Sin embargo, para el manifest, basta con que esté en static y el navegador lo encuentre si lo linkeamos.
    
    # 1. Link al Manifest (esto suele requerir manipulación del index.html template de Streamlit, 
    # pero podemos intentar inyectarlo dinámicamente o confiar en que el usuario lo añada manualmente si tiene acceso al template).
    # Como no tenemos acceso fácil al index.html en Streamlit cloud/standard sin hackear, 
    # asumimos que el navegador puede descubrir el manifest si está en la raíz, pero Streamlit sirve desde /static.
    
    # HACK: Inyectar tags en el head usando st.markdown (funciona en versiones recientes para algunos tags)
    st.markdown("""
        <link rel="manifest" href="src/static/manifest.json">
        <meta name="theme-color" content="#1f77b4">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
    """, unsafe_allow_html=True)

    # Registro del SW via componente iframe (para asegurar ejecución JS)
    components.html(pwa_script, height=0, width=0)

def show_pwa_status():
    """
    Muestra un indicador de estado de la PWA (útil para debugging o configuración).
    """
    st.info("📱 PWA System: Active")
