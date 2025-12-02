import streamlit as st
import time
from db import get_client
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def check_database_connection():
    """
    Verifica la conexión a la base de datos con un indicador visual (spinner).
    Si falla, muestra un mensaje de error detallado en la UI.
    
    Returns:
        bool: True si la conexión es exitosa, False si falla.
    """
    # Usamos un contenedor vacío para que el spinner no desplace el contenido bruscamente
    status_container = st.empty()
    
    try:
        with status_container:
            with st.spinner("Conectando a la base de datos..."):
                # Intentamos obtener el cliente y hacer un ping
                client = get_client()
                # Forzamos una operación para verificar la conexión real
                client.admin.command('ping')
                
        # Si llegamos aquí, la conexión es exitosa. Limpiamos el contenedor.
        status_container.empty()
        return True
        
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
        # En caso de error, mostramos el mensaje en el contenedor
        status_container.error(f"❌ Error de conexión a la base de datos:\n\n{str(e)}")
        return False
