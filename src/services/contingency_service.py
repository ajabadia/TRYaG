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
        st.toast("⚠️ MODO MANUAL ACTIVADO: Análisis IA deshabilitado", icon="🛠️")
    else:
        st.toast("✅ MODO AUTOMÁTICO: IA Reactivada", icon="🤖")

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
    Sincroniza los datos locales con el servidor central (MongoDB).
    """
    _ensure_initialized()
    unsynced = [r for r in st.session_state.local_triage_cache if not r.get('synced')]
    if not unsynced:
        st.info("No hay datos pendientes de sincronización.")
        return

    from services.patient_flow_service import save_triage_data
    
    with st.spinner(f"Sincronizando {len(unsynced)} registros con la base de datos..."):
        success_count = 0
        failed_count = 0
        
        for record in unsynced:
            # Reconstruir estructura esperada por save_triage_data
            # El registro local tiene: {id, timestamp, patient, result, synced}
            # save_triage_data espera: {datos_paciente: ..., resultado: ..., contingency_mode: True}
            
            patient_data = record.get('patient', {})
            triage_result = record.get('result', {})
            
            # Asegurar que patient_code existe
            patient_code = patient_data.get('patient_code')
            if not patient_code:
                # Intentar recuperar de ID o generar uno temporal si es anónimo
                patient_code = f"ANON-{record['id']}"
            
            full_data = {
                "datos_paciente": patient_data,
                "resultado": triage_result,
                "evaluator_id": "system_offline",
                "contingency_mode": True,
                "is_training": st.session_state.get('training_mode', False) # Heredar estado actual o guardar en record
            }
            
            if save_triage_data(patient_code, full_data):
                record['synced'] = True
                success_count += 1
            else:
                failed_count += 1
        
        # Limpiar solo los sincronizados
        st.session_state.local_triage_cache = [r for r in st.session_state.local_triage_cache if not r.get('synced')]
        
        if success_count > 0:
            st.success(f"✅ {success_count} registros sincronizados correctamente.")
        
        if failed_count > 0:
            st.error(f"❌ {failed_count} registros fallaron al sincronizar. Se mantienen en caché local.")
