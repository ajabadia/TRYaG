# path: src/utils/patient_utils.py
# Creado: 2025-11-26
"""
Utilidades para la gestión y comparación de datos de pacientes.
"""
import streamlit as st
from typing import Dict, Any, Optional

def compare_patient_data(data_form: dict, data_db: dict) -> Dict[str, Any]:
    """
    Compara datos del formulario con datos en BD.
    Retorna dict con campos modificados.
    
    Args:
        data_form: Datos provenientes del formulario (inputs)
        data_db: Datos originales de la base de datos
        
    Returns:
        Diccionario con los cambios detectados:
        {
            'campo': {'old': valor_anterior, 'new': valor_nuevo}
        }
    """
    changes = {}
    
    # Campos simples a comparar
    fields_map = {
        'nombre': 'nombre',
        'apellido1': 'apellido1',
        'apellido2': 'apellido2',
        'fecha_nacimiento': 'fecha_nacimiento',
        'num_ss': 'num_ss',
        'num_identificacion': 'num_identificacion',
        'tipo_identificacion': 'tipo_identificacion'
    }
    
    for form_field, db_field in fields_map.items():
        val_form = data_form.get(form_field)
        val_db = data_db.get(db_field)
        
        # Normalización básica para comparación
        if isinstance(val_form, str):
            val_form = val_form.strip()
        if isinstance(val_db, str):
            val_db = val_db.strip()
            
        # Manejo de fechas
        if hasattr(val_form, 'date') and hasattr(val_db, 'date'):
             if val_form != val_db: # Si son datetimes
                 # Comparar solo fecha si uno es date y otro datetime o ambos datetime
                 # Asumimos que vienen normalizados, pero por si acaso
                 pass
        
        # Comparación directa
        if val_form != val_db:
            # Ignorar diferencias de None vs ""
            if not val_form and not val_db:
                continue
                
            changes[form_field] = {
                'old': val_db,
                'new': val_form
            }
    
    # Contactos (comparación especial)
    contacts_form = data_form.get('contact_info', [])
    contacts_db = data_db.get('contact_info', [])
    
    if contacts_form != contacts_db:
        changes['contact_info'] = {
            'old': contacts_db,
            'new': contacts_form
        }
    
    return changes

def prompt_update_confirmation(changes: Dict) -> Optional[bool]:
    """
    Muestra modal preguntando si actualizar datos.
    
    Args:
        changes: Diccionario de cambios detectados
        
    Returns:
        True si confirma, False si cancela, None si no decide aún
    """
    if not changes:
        return True
        
    st.warning("⚠️ Se han detectado cambios en los datos del paciente respecto a la base de datos.")
    
    with st.expander("Ver detalles de cambios", expanded=True):
        for field, change in changes.items():
            st.markdown(f"**{field}:**")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Anterior")
                st.code(str(change['old']))
            with col2:
                st.caption("Nuevo")
                st.code(str(change['new']))
    
    st.markdown("¿Desea actualizar los datos del paciente con la nueva información?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Actualizar Datos", type="primary", use_container_width=True, key="confirm_update_patient"):
            return True
    with col2:
        if st.button("❌ Mantener Datos Originales", type="secondary", use_container_width=True, key="cancel_update_patient"):
            return False
    
    return None
