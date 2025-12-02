import streamlit as st
from utils.icons import render_icon

def render_disposition_form(disabled: bool = False):
    """
    Renderiza el formulario de Planificación de Salida y Órdenes Iniciales (Fase 6).
    Incluye: Órdenes Médicas Iniciales y Planificación de Alta.
    """
    reset_count = st.session_state.get('reset_counter', 0)
    
    with st.container(border=True):
        c_icon, c_title = st.columns([1, 20])
        with c_icon:
            render_icon("clipboard", size=24)
        with c_title:
            st.header("4. Órdenes y Planificación")

        # --- 1. ÓRDENES INICIALES ---
        st.markdown("##### 💊 Órdenes Iniciales (Protocolo)")
        
        c_ord1, c_ord2 = st.columns(2)
        with c_ord1:
            st.session_state.datos_paciente['order_diet'] = st.selectbox(
                "Dieta / Nutrición",
                ["NPO (Nada por boca)", "Dieta Absoluta", "Líquidos Claros", "Dieta Blanda", "Dieta Normal", "Diabética"],
                index=0, disabled=disabled, key=f"ord_diet_{reset_count}"
            )
            st.session_state.datos_paciente['order_iv'] = st.checkbox("Acceso Venoso (IV) Requerido", value=st.session_state.datos_paciente.get('order_iv', False), disabled=disabled, key=f"ord_iv_{reset_count}")
            
        with c_ord2:
            st.session_state.datos_paciente['order_labs'] = st.multiselect(
                "Solicitud de Pruebas (Protocolo)",
                ["Hemograma", "Bioquímica", "Coagulación", "Gasometría", "ECG", "RX Tórax", "Orina"],
                default=st.session_state.datos_paciente.get('order_labs', []),
                disabled=disabled, key=f"ord_labs_{reset_count}"
            )
            st.session_state.datos_paciente['order_meds_stat'] = st.text_input("Medicación STAT (Inmediata)", placeholder="Ej. Analgesia, Antitérmico...", disabled=disabled, key=f"ord_meds_{reset_count}")

        st.divider()

        # --- 2. PLANIFICACIÓN DE ALTA (DISCHARGE PLANNING) ---
        st.markdown("##### 🏠 Planificación de Alta")
        
        c_dis1, c_dis2 = st.columns(2)
        with c_dis1:
            st.session_state.datos_paciente['dis_needs'] = st.multiselect(
                "Necesidades al Alta Previstas",
                ["Transporte Sanitario", "Oxígeno Domiciliario", "Curas/Enfermería", "Rehabilitación", "Trabajo Social"],
                default=st.session_state.datos_paciente.get('dis_needs', []),
                disabled=disabled, key=f"dis_needs_{reset_count}"
            )
        
        with c_dis2:
            st.session_state.datos_paciente['dis_barriers'] = st.text_area(
                "Barreras para el Alta",
                placeholder="Ej. Vive solo, escaleras, falta de cuidador...",
                height=68,
                disabled=disabled, key=f"dis_barriers_{reset_count}"
            )

    st.markdown('<div class="debug-footer">src/components/triage/disposition_form.py</div>', unsafe_allow_html=True)
