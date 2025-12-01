import streamlit as st
from utils.icons import render_icon

def render_nursing_assessment_form(disabled: bool = False):
    """
    Renderiza el formulario de Valoración de Enfermería (Fase 5).
    Incluye: Piel, Riesgos (Caídas, Aspiración), Seguridad y Pertenencias.
    """
    # Recuperar contador para keys únicas
    reset_count = st.session_state.get('reset_counter', 0)
    
    with st.container(border=True):
        # Cabecera
        c_icon, c_title = st.columns([1, 20])
        with c_icon:
            render_icon("activity", size=24) # Icono genérico de actividad/enfermería
        with c_title:
            st.header("3. Valoración de Enfermería")

        # --- 1. VALORACIÓN DE PIEL (INTEGUMENTARIA) ---
        st.markdown("##### 🧴 Piel y Tegumentos")
        
        c_skin1, c_skin2 = st.columns(2)
        with c_skin1:
            st.session_state.datos_paciente['skin_integrity'] = st.selectbox(
                "Integridad Cutánea",
                ["Intacta", "Herida/Abrasión", "Úlcera por Presión", "Quemadura", "Erupción/Rash", "Hematoma"],
                index=0, disabled=disabled, key=f"skin_int_{reset_count}"
            )
            
            # Si no está intacta, pedir detalles
            if st.session_state.datos_paciente['skin_integrity'] != "Intacta":
                st.session_state.datos_paciente['skin_details'] = st.text_input("Detalles / Localización", placeholder="Ej. Sacro, Talón derecho...", disabled=disabled, key=f"skin_det_{reset_count}")
        
        with c_skin2:
            st.session_state.datos_paciente['skin_color'] = st.selectbox(
                "Coloración / Temperatura",
                ["Normal/Rosada", "Pálida", "Cianótica", "Ictérica", "Eritematosa", "Fría/Sudorosa"],
                index=0, disabled=disabled, key=f"skin_col_{reset_count}"
            )
            st.session_state.datos_paciente['skin_edema'] = st.checkbox("Edema Presente", value=st.session_state.datos_paciente.get('skin_edema', False), disabled=disabled, key=f"skin_edema_{reset_count}")
            if st.session_state.datos_paciente['skin_edema']:
                 st.session_state.datos_paciente['skin_edema_loc'] = st.text_input("Localización Edema", placeholder="Ej. MMII, Generalizado...", disabled=disabled, key=f"skin_edema_loc_{reset_count}")

        st.divider()

        # --- 2. ESCALAS DE RIESGO ---
        st.markdown("##### ⚠️ Escalas de Riesgo")
        
        c_risk1, c_risk2 = st.columns(2)
        with c_risk1:
            # Riesgo de Caídas (Simplificado Morse/Hendrich)
            st.markdown("**Riesgo de Caídas**")
            fall_hist = st.checkbox("Historia de Caídas (últimos 3 meses)", value=st.session_state.datos_paciente.get('fall_hist', False), disabled=disabled, key=f"fall_hist_{reset_count}")
            fall_help = st.checkbox("Necesita ayuda para deambular", value=st.session_state.datos_paciente.get('fall_help', False), disabled=disabled, key=f"fall_help_{reset_count}")
            
            # Cálculo simple
            fall_risk_level = "Bajo"
            if fall_hist and fall_help: fall_risk_level = "Alto"
            elif fall_hist or fall_help: fall_risk_level = "Medio"
            
            st.session_state.datos_paciente['fall_risk'] = fall_risk_level
            
            color_risk = {"Bajo": "green", "Medio": "orange", "Alto": "red"}.get(fall_risk_level, "gray")
            st.caption(f"Nivel de Riesgo: :{color_risk}[{fall_risk_level.upper()}]")
            if fall_risk_level == "Alto":
                st.warning("Protocolo Caídas: Barandillas arriba, timbre a mano.")

        with c_risk2:
            # Riesgo de Aspiración / Disfagia
            st.markdown("**Riesgo de Aspiración**")
            dysphagia = st.checkbox("Signos de Disfagia / Tos al comer", value=st.session_state.datos_paciente.get('nut_disfagia', False), disabled=disabled, key=f"risk_dys_{reset_count}") # Reutiliza o sincroniza con nut_disfagia
            npo = st.checkbox("Mantener NPO (Nada por boca)", value=st.session_state.datos_paciente.get('order_npo', False), disabled=disabled, key=f"risk_npo_{reset_count}")
            
            st.session_state.datos_paciente['nut_disfagia'] = dysphagia
            st.session_state.datos_paciente['order_npo'] = npo

        st.divider()

        # --- 3. SEGURIDAD Y PERTENENCIAS ---
        st.markdown("##### 🔒 Seguridad y Pertenencias")
        
        c_safe1, c_safe2 = st.columns(2)
        with c_safe1:
            st.session_state.datos_paciente['id_bracelet'] = st.checkbox("Pulsera Identificativa Colocada", value=st.session_state.datos_paciente.get('id_bracelet', False), disabled=disabled, key=f"safe_id_{reset_count}")
            if not st.session_state.datos_paciente['id_bracelet']:
                st.error("⚠️ Pendiente: Colocar pulsera ID")
                
        with c_safe2:
            st.session_state.datos_paciente['belongings'] = st.text_area("Inventario de Pertenencias / Valores", value=st.session_state.datos_paciente.get('belongings', ''), height=68, placeholder="Gafas, Dentadura, Móvil...", disabled=disabled, key=f"safe_bel_{reset_count}")
            st.session_state.datos_paciente['family_notified'] = st.checkbox("Familiares Notificados", value=st.session_state.datos_paciente.get('family_notified', False), disabled=disabled, key=f"safe_fam_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/nursing_form.py</div>', unsafe_allow_html=True)
