import streamlit as st
import streamlit.components.v1 as components

def render_pwa_installer():
    """
    Inyecta el código necesario para registrar el Service Worker y habilitar la instalación PWA.
    Debe llamarse al inicio de la aplicación (app.py).
    """
    
    # HTML/JS para registrar el Service Worker
    # HTML/JS para registrar el Service Worker
    # Streamlit sirve archivos de 'static' en 'app/static' cuando está en la carpeta del script
    pwa_script = """
    <script src="app/static/js/offline_db.js"></script>
    <script src="app/static/js/push_notifications.js"></script>
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('app/static/sw.js').then(function(registration) {
                    console.log('ServiceWorker registration successful with scope: ', registration.scope);
                    window.pwaRegistration = registration;
                }, function(err) {
                    console.log('ServiceWorker registration failed: ', err);
                });
            });
        }
    </script>
    """
    
    # HACK: Inyectar tags en el head usando st.markdown
    st.markdown("""
        <link rel="manifest" href="app/static/manifest.json">
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
