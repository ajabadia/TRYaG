import streamlit as st
from db.repositories.insurers import get_insurers_repository

def render_admin_data_form(reset_count: int, disabled: bool = False):
    """
    Renderiza el formulario de datos administrativos y logística.
    Incluye la selección de aseguradora.
    """
    with st.expander("📋 Datos Administrativos y Logística", expanded=False):
        c_adm1, c_adm2 = st.columns(2)
        
        with c_adm1:
            st.session_state.datos_paciente['fuente_informacion'] = st.selectbox(
                "Fuente de Información", 
                ["Paciente", "Familiar/Cuidador", "Servicio de Emergencias (EMS)", "Testigos", "Otro"],
                index=0, disabled=disabled, key=f"admin_source_{reset_count}"
            )
            
            st.session_state.datos_paciente['referencia'] = st.text_input(
                "Médico/Centro Referente", 
                value=st.session_state.datos_paciente.get('referencia', ''),
                placeholder="Ej. CAP Norte, Dr. Smith",
                disabled=disabled, key=f"admin_ref_{reset_count}"
            )

        with c_adm2:
            st.markdown("##### 🏥 Cobertura Sanitaria")
            
            # Recuperar estado actual
            insurance_info = st.session_state.datos_paciente.get('insurance_info', {})
            has_insurance = insurance_info.get('has_insurance', False)
            
            # 1. ¿Tiene seguro?
            tiene_seguro = st.radio(
                "¿Aseguradora o Privado?",
                ["Privado", "Aseguradora/Mutua"],
                index=1 if has_insurance else 0,
                horizontal=True,
                disabled=disabled,
                key=f"admin_has_insurance_radio_{reset_count}"
            )
            
            if tiene_seguro == "Aseguradora/Mutua":
                repo_insurers = get_insurers_repository()
                insurers_list = repo_insurers.get_all(active_only=True)
                
                # Preparar opciones
                options = ["Seleccionar..."] + [i['name'] for i in insurers_list]
                
                # Pre-selección
                current_insurer_name = insurance_info.get('insurer_name')
                index_sel = 0
                if current_insurer_name in options:
                    index_sel = options.index(current_insurer_name)
                
                selected_insurer_name = st.selectbox(
                    "Seleccione la Compañía", 
                    options, 
                    index=index_sel, 
                    disabled=disabled,
                    key=f"admin_insurer_select_{reset_count}"
                )
                
                if selected_insurer_name != "Seleccionar...":
                    # Buscar objeto completo
                    insurer_obj = next((i for i in insurers_list if i['name'] == selected_insurer_name), None)
                    
                    if insurer_obj:
                        # Mostrar Logo si existe
                        if insurer_obj.get('logo_url'):
                            st.image(insurer_obj['logo_url'], width=100)
                            
                        # Guardar selección en datos_paciente
                        st.session_state.datos_paciente['insurance_info'] = {
                            "has_insurance": True,
                            "insurer_id": str(insurer_obj['_id']),
                            "insurer_name": insurer_obj['name'],
                            "logo_url": insurer_obj.get('logo_url'),
                            "type": "Aseguradora" if insurer_obj.get('is_insurer') else "Mutua"
                        }
                        # Compatibilidad legacy (por si acaso se usa 'seguro' string en otro lado)
                        st.session_state.datos_paciente['seguro'] = insurer_obj['name']
                else:
                     # Reset si vuelve a seleccionar...
                     if 'insurance_info' in st.session_state.datos_paciente:
                         st.session_state.datos_paciente['insurance_info'] = {}
                         st.session_state.datos_paciente['seguro'] = ""

            else:
                # Privado
                st.session_state.datos_paciente['insurance_info'] = {
                    "has_insurance": False,
                    "type": "Privado"
                }
                st.session_state.datos_paciente['seguro'] = "Privado"
    
    st.markdown('<div style="color: #ccc; font-size: 0.6em; text-align: right; margin-top: 5px;">src/components/triage/admin_data_form.py</div>', unsafe_allow_html=True)

    st.markdown('<div class="debug-footer">src/components/triage/admin_data_form.py</div>', unsafe_allow_html=True)
