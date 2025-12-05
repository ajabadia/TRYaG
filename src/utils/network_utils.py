# path: src/utils/network_utils.py
import streamlit as st
import warnings

def get_client_ip():
    """
    Intenta obtener la IP del cliente desde los headers de la petición.
    Funciona mejor detrás de un proxy (Nginx/Cloud) usando X-Forwarded-For.
    """
    try:
        # 1. Intentar obtener headers del contexto (Streamlit >= 1.33)
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            if "X-Forwarded-For" in headers:
                return headers["X-Forwarded-For"].split(",")[0].strip()
            if "X-Real-Ip" in headers:
                return headers["X-Real-Ip"]
            
            # Si estamos aquí, tenemos context pero no headers de IP (ej: local)
            return "unknown_ip (local)"
        
        # 2. Fallback solo para versiones muy antiguas (< 1.33)
        # Esto no debería ejecutarse en tu versión actual
        try:
            from streamlit.web.server.websocket_headers import _get_websocket_headers
            headers = _get_websocket_headers()
            if headers:
                if "X-Forwarded-For" in headers:
                    return headers["X-Forwarded-For"].split(",")[0].strip()
                if "X-Real-Ip" in headers:
                    return headers["X-Real-Ip"]
        except ImportError:
            pass
            
        return "unknown_ip"
    except Exception as e:
        return f"error_getting_ip"
