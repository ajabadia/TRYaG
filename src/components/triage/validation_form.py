# path: src/components/triage/validation_form.py
# Creado: 2025-11-21
# Última modificación: 2025-11-22
"""
Componente para la validación humana de la decisión de triaje.
"""
import streamlit as st
from datetime import datetime
from core.data_handler import guardar_auditoria
from utils.icons import render_icon
from utils.session_utils import reset_session_state

def render_validation_form():
    """
    Renderiza el formulario de validación humana.
    """
    if st.session_state.resultado and st.session_state.resultado.get("status") == "SUCCESS":
        st.divider()
        
        # Cabecera con icono
        c_head_icon, c_head_text = st.columns([1, 20])
        with c_head_icon:
            render_icon("check", size=24, color="#28a745")
        with c_head_text:
            st.header("3. Validación Humana (Human-in-the-Loop)")
            
        # Obtener contador de reset
        reset_count = st.session_state.get('reset_counter', 0)

        resultado = st.session_state.resultado
        datos_paciente = st.session_state.datos_paciente
        
        # --- MOSTRAR NIVEL SUGERIDO (Prominente) ---
        nivel_info = resultado.get('nivel', {})
        nivel_texto = nivel_info.get('text', 'N/A')
        nivel_color = nivel_info.get('color', 'grey')
        
        st.markdown(
            f"""
            <div style="background-color: {nivel_color}; color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                <h3 style="margin:0;">IA Sugiere: {nivel_texto}</h3>
                <p style="margin:5px 0 0 0;">{ " | ".join(resultado.get('razones', [])) }</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.caption("Debe validar o corregir la decisión de la IA.")
        
        # Opciones de Decisión
        opciones = ["Confirmar Nivel Sugerido", "Modificar Nivel", "No aplica (Rechazar/Derivar)"]
        decision = st.radio("Decisión Clínica", opciones, key=f"decision_clinica_{reset_count}")
        
        datos_auditoria = {
            "timestamp": datetime.now().isoformat(),
            "motivo_consulta": datos_paciente.get('texto_medico', ''),
            "edad": datos_paciente.get('edad'),
            "gender": datos_paciente.get('gender'),
            "dolor": datos_paciente.get('dolor'),
            "antecedentes": datos_paciente.get('antecedentes', ''),
            "alergias": datos_paciente.get('alergias_info_completa', ''),
            "signos_vitales": datos_paciente.get('vital_signs', {}),
            "import_files": len(datos_paciente.get('imagenes', [])),
            "ia_files": len(datos_paciente.get('imagenes_confirmadas_ia', [])),
            "sugerencia_ia": nivel_texto,
            "razones_ia": " | ".join(resultado.get('razones', [])),
            "calificacion_humana": st.session_state.get('calificacion_humana', 'No calificado'),
            "patient_code": st.session_state.triage_patient.get('patient_code') if st.session_state.get('triage_patient') else None
        }

        # Comprobar si ya se ha completado la validación en esta sesión
        if st.session_state.get('validation_complete', False):
            msg_type = st.session_state.get('validation_msg_type', 'success')
            msg_text = st.session_state.get('validation_msg', 'Validación completada.')
            
            c_icon, c_text = st.columns([1, 20])
            with c_icon:
                render_icon("check" if msg_type == 'success' else "warning", size=20, color="green" if msg_type == 'success' else "#ffc107")
            with c_text:
                if msg_type == 'success':
                    st.success(msg_text)
                else:
                    st.warning(msg_text)
            return

        # --- Lógica de Decisión ---
        
        if decision == "Confirmar Nivel Sugerido":
            if st.button("Confirmar y Continuar", type="primary", use_container_width=True):
                datos_auditoria.update({"decision_humana": "Confirmado", "nivel_corregido": nivel_texto, "justificacion_humana": ""})
                guardar_auditoria(datos_auditoria, st.session_state)
                
                st.session_state.validation_complete = True
                st.session_state.validation_msg = "Triaje validado. Proceda a la derivación."
                st.session_state.validation_msg_type = "success"
                st.rerun()

        elif decision == "Modificar Nivel":
            niveles_descripcion = {
                "Nivel I (Resucitación)": "Riesgo vital inmediato.",
                "Nivel II (Emergencia)": "Alto riesgo, posible compromiso vital.",
                "Nivel III (Urgencia)": "Necesita múltiples exploraciones, sin riesgo vital.",
                "Nivel IV (Menos Urgente)": "Lesión menor, exploración simple.",
                "Nivel V (No Urgente)": "Atención primaria."
            }
            nuevo_nivel_display = st.selectbox("Seleccione Nivel Real", list(niveles_descripcion.keys()))
            st.info(f"**Definición:** {niveles_descripcion[nuevo_nivel_display]}")
            justificacion = st.text_input("Justificación del cambio (obligatoria)")
            
            if st.button("Guardar Cambio y Continuar", type="primary", use_container_width=True):
                if not justificacion:
                    st.error("La justificación es obligatoria al modificar el nivel.")
                else:
                    nivel_humano_norm = nuevo_nivel_display.split(' (')[0]
                    datos_auditoria.update({"decision_humana": "Modificado", "nivel_corregido": nivel_humano_norm, "justificacion_humana": justificacion})
                    guardar_auditoria(datos_auditoria, st.session_state)
                    
                    st.session_state.validation_complete = True
                    st.session_state.validation_msg = f"Nivel modificado a {nivel_humano_norm}. Proceda a la derivación."
                    st.session_state.validation_msg_type = "warning"
                    st.rerun()

        elif decision == "No aplica (Rechazar/Derivar)":
            st.warning("El paciente no cumple criterios para Traumatología.")
            col_rej, col_der = st.columns(2)
            
            with col_rej:
                if st.button("🚫 Rechazar Paciente", use_container_width=True):
                    # Lógica de rechazo directo
                    from services.flow_manager import rechazar_paciente
                    from services.permissions_service import get_current_user
                    user = get_current_user().get("username", "unknown")
                    
                    success, msg = rechazar_paciente(st.session_state.triage_patient['patient_code'], "No es caso de traumatología", user)
                    if success:
                        st.success("Paciente rechazado correctamente.")
                        # Limpiar y volver
                        st.session_state.triage_step = 1
                        st.session_state.triage_patient = None
                        st.session_state.resultado = None
                        st.rerun()
                    else:
                        st.error(f"Error al rechazar: {msg}")

            with col_der:
                if st.button("👨‍⚕️ Derivar a Consulta/Ingreso", type="primary", use_container_width=True):
                    # Cambiar modo a derivación especial
                    st.session_state.triage_special_derivation = True
                    st.session_state.validation_complete = True # Marcar validado para permitir avanzar (aunque sea derivación especial)
                    st.session_state.validation_msg = "Procediendo a derivación externa..."
                    st.rerun()
            
            if st.session_state.get('triage_special_derivation'):
                 st.info("Seleccione la Consulta de Ingreso en el siguiente paso.")
                 if st.button("Ir a Derivación →", type="primary"):
                     st.session_state.triage_step = 3 # Ir a paso de derivación
                     st.rerun()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/validation_form.py</div>', unsafe_allow_html=True)
