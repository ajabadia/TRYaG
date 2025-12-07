import streamlit as st
from db.repositories.people import get_people_repository
from ui.config.people_manager import person_dialog

def render_patient_search(key_prefix: str = "search") -> dict | None:
    """
    Componente reutilizable para búsqueda y selección de pacientes.
    
    Args:
        key_prefix: Prefijo para claves de estado de Streamlit.
        
    Returns:
        dict | None: Objeto persona seleccionado o None.
    """
    repo = get_people_repository()
    
    # Check if a patient is already selected in this context
    selected_key = f"{key_prefix}_selected_patient"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = None

    # Si ya hay uno seleccionado, permitir "Cambiar"
    selected = st.session_state[selected_key]
    if selected:
        c1, c2 = st.columns([4, 1])
        with c1:
            name = f"{selected.get('nombre')} {selected.get('apellido1')} {selected.get('apellido2') or ''}"
            st.success(f"Paciente Seleccionado: **{name}** ({selected.get('patient_code')})")
        with c2:
            if st.button("🔄 Cambiar", key=f"{key_prefix}_change_btn"):
                st.session_state[selected_key] = None
                st.rerun()
        return selected

    # Si no, mostrar buscador
    with st.container(border=True):
        st.markdown("**🔍 Búsqueda de Paciente**")
        search_term = st.text_input("Buscar por Nombre, DNI, SS...", 
                                  placeholder="Escriba al menos 3 caracteres", 
                                  key=f"{key_prefix}_term")
        
        if search_term and len(search_term) >= 3:
            results = repo.search_by_name(search_term)
            
            if results:
                st.caption(f"Encontrados {len(results)} resultados:")
                for p in results:
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            nombre_completo = f"{p.get('nombre')} {p.get('apellido1')} {p.get('apellido2') or ''}".strip()
                            st.markdown(f"**{nombre_completo}**")
                            
                            ids = []
                            if p.get('num_ss'): ids.append(f"SS: {p.get('num_ss')}")
                            if p.get('identification_number'): ids.append(f"ID: {p.get('identification_number')}")
                            
                            st.caption(f"Código: `{p.get('patient_code')}` | {' | '.join(ids)}")
                            
                        with c2:
                            if st.button("Seleccionar", key=f"{key_prefix}_sel_{p['_id']}", use_container_width=True):
                                st.session_state[selected_key] = p
                                st.rerun()
            else:
                st.info("No se encontraron resultados.")
        elif search_term:
            st.caption("Escriba al menos 3 caracteres.")
            
    return None
