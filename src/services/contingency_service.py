import streamlit as st
import json
from datetime import datetime

# Simulación de almacenamiento local (Browser LocalStorage o SessionState persistente)
def _ensure_initialized():
    if 'local_triage_cache' not in st.session_state:
        st.session_state.local_triage_cache = []
    if 'contingency_mode' not in st.session_state:
        st.session_state.contingency_mode = False

def set_contingency_mode(enabled: bool):
    """Activa o desactiva el modo de contingencia."""
    _ensure_initialized()
    st.session_state.contingency_mode = enabled
    if enabled:
        st.toast("⚠️ MODO CONTINGENCIA ACTIVADO: Funcionalidad Reducida", icon="📴")
    else:
        st.toast("✅ CONEXIÓN RESTABLECIDA: Sincronizando datos...", icon="📶")
        sync_local_data()

def is_contingency_active() -> bool:
    """Retorna True si el modo de contingencia está activo."""
    _ensure_initialized()
    return st.session_state.get('contingency_mode', False)

def save_triage_locally(patient_data: dict, triage_result: dict):
    """
    Guarda el registro de triaje en la caché local cuando no hay conexión.
    """
    _ensure_initialized()
    record = {
        "id": f"LOC-{int(datetime.now().timestamp())}",
        "timestamp": datetime.now().isoformat(),
        "patient": patient_data,
        "result": triage_result,
        "synced": False
    }
    st.session_state.local_triage_cache.append(record)
    st.success(f"Registro guardado localmente (ID: {record['id']}). Pendiente de sincronización.")

def get_unsynced_count() -> int:
    """Retorna el número de registros pendientes de sincronización."""
    _ensure_initialized()
    return len([r for r in st.session_state.local_triage_cache if not r['synced']])

def sync_local_data():
    """
    Simula la sincronización de datos con el servidor central.
    """
    _ensure_initialized()
    unsynced = [r for r in st.session_state.local_triage_cache if not r['synced']]
    if not unsynced:
        st.info("No hay datos pendientes de sincronización.")
        return

    # Simular envío
    import time
    with st.spinner(f"Sincronizando {len(unsynced)} registros..."):
        time.sleep(1.5) # Simular latencia
        
        # Marcar como sincronizados (en un caso real, se enviarían a la API)
        for r in st.session_state.local_triage_cache:
            r['synced'] = True
            
        # Limpiar caché (o mantener historial)
        st.session_state.local_triage_cache = [] 
        st.success("✅ Sincronización completada correctamente.")
