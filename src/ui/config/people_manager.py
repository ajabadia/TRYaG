import streamlit as st
from datetime import datetime, date
from db.repositories.people import get_people_repository

from services.patient_service import generar_codigo_paciente

def render_person_form(person_data=None, key_prefix="person_form"):
    """
    Renderiza un formulario para crear o editar una persona.
    Retorna el diccionario con los datos si se guarda, o None.
    """
    is_new = person_data is None
    person_data = person_data or {}
    
    with st.container(border=True):
        st.markdown("#### 👤 Datos Personales")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre *", value=person_data.get("nombre", ""), key=f"{key_prefix}_nombre")
            apellido1 = st.text_input("Primer Apellido *", value=person_data.get("apellido1", ""), key=f"{key_prefix}_ap1")
            apellido2 = st.text_input("Segundo Apellido", value=person_data.get("apellido2", ""), key=f"{key_prefix}_ap2")
            
            gender_opts = ["Hombre", "Mujer", "Otro", "No Especificado"]
            current_gender = person_data.get("gender", "No Especificado")
            if current_gender not in gender_opts:
                current_gender = "No Especificado"
                
            gender = st.selectbox("Sexo / Género", gender_opts, 
                                index=gender_opts.index(current_gender),
                                key=f"{key_prefix}_gender")
        
        with col2:
            # --- Identificaciones (Múltiples) ---
            st.markdown("##### 🪪 Identificaciones")
            
            # Inicializar lista en session_state
            ids_key = f"{key_prefix}_ids_list"
            if ids_key not in st.session_state:
                st.session_state[ids_key] = person_data.get("identificaciones", []) or [{"type": "DNI", "value": ""}]

            # Renderizar lista
            ids_to_remove = []
            updated_ids = []
            
            for i, ident in enumerate(st.session_state[ids_key]):
                c_type, c_val, c_del = st.columns([1.5, 2.5, 0.5])
                with c_type:
                    new_type = st.selectbox("Tipo", ["DNI", "NIE", "PASAPORTE", "OTRO"], 
                                          index=["DNI", "NIE", "PASAPORTE", "OTRO"].index(ident.get("type", "DNI")) if ident.get("type") in ["DNI", "NIE", "PASAPORTE", "OTRO"] else 0,
                                          key=f"{key_prefix}_id_type_{i}", label_visibility="collapsed")
                with c_val:
                    new_val = st.text_input("Valor", value=ident.get("value", ""), 
                                          key=f"{key_prefix}_id_val_{i}", label_visibility="collapsed", placeholder="Número ID")
                with c_del:
                    if st.button("🗑️", key=f"{key_prefix}_del_id_{i}"):
                        ids_to_remove.append(i)
                
                updated_ids.append({"type": new_type, "value": new_val})
            
            # Procesar eliminaciones
            if ids_to_remove:
                for idx in sorted(ids_to_remove, reverse=True):
                    updated_ids.pop(idx)
                st.session_state[ids_key] = updated_ids
                st.rerun()
            
            # Botón Añadir
            if st.button("➕ Añadir ID", key=f"{key_prefix}_add_id"):
                updated_ids.append({"type": "OTRO", "value": ""})
                st.session_state[ids_key] = updated_ids
                st.rerun()

            # Actualizar estado con valores editados
            st.session_state[ids_key] = updated_ids
            
            
            # --- Fecha Nacimiento ---
            st.markdown("##### 📅 Nacimiento")
            fnac_val = person_data.get("fecha_nacimiento")
            if isinstance(fnac_val, datetime):
                fnac_val = fnac_val.date()
            elif isinstance(fnac_val, str):
                try:
                    fnac_val = datetime.fromisoformat(fnac_val).date()
                except:
                    fnac_val = None
            
            fecha_nac = st.date_input("Fecha de Nacimiento", 
                                      value=fnac_val,
                                      min_value=date(1900, 1, 1),
                                      max_value=date.today(),
                                      key=f"{key_prefix}_fnac",
                                      label_visibility="collapsed")

        # --- Contacto (Múltiples) ---
        st.markdown("##### 📞 Información de Contacto")
        
        contacts_key = f"{key_prefix}_contacts_list"
        if contacts_key not in st.session_state:
            st.session_state[contacts_key] = person_data.get("contact_info", []) or [{"type": "phone", "value": "", "primary": True}]

        contacts_to_remove = []
        updated_contacts = []
        
        for i, cont in enumerate(st.session_state[contacts_key]):
            c_type, c_val, c_prim, c_del = st.columns([1.5, 2, 1, 0.5])
            with c_type:
                new_type = st.selectbox("Tipo", ["phone", "mobile", "email"], 
                                      index=["phone", "mobile", "email"].index(cont.get("type", "phone")) if cont.get("type") in ["phone", "mobile", "email"] else 0,
                                      key=f"{key_prefix}_cont_type_{i}", label_visibility="collapsed")
            with c_val:
                new_val = st.text_input("Valor", value=cont.get("value", ""), 
                                      key=f"{key_prefix}_cont_val_{i}", label_visibility="collapsed", placeholder="Contacto")
            with c_prim:
                new_prim = st.checkbox("Principal", value=cont.get("primary", False), key=f"{key_prefix}_cont_prim_{i}")
            with c_del:
                if st.button("🗑️", key=f"{key_prefix}_del_cont_{i}"):
                    contacts_to_remove.append(i)
            
            updated_contacts.append({"type": new_type, "value": new_val, "primary": new_prim})

        if contacts_to_remove:
            for idx in sorted(contacts_to_remove, reverse=True):
                updated_contacts.pop(idx)
            st.session_state[contacts_key] = updated_contacts
            st.rerun()

        if st.button("➕ Añadir Contacto", key=f"{key_prefix}_add_cont"):
            updated_contacts.append({"type": "phone", "value": "", "primary": False})
            st.session_state[contacts_key] = updated_contacts
            st.rerun()
            
        st.session_state[contacts_key] = updated_contacts


        if st.button("💾 Guardar Persona", type="primary", key=f"{key_prefix}_save"):
            # Validaciones básicas
            final_ids = st.session_state[ids_key]
            final_contacts = st.session_state[contacts_key]
            
            # Validar que haya al menos un ID con valor
            has_valid_id = any(i.get("value") for i in final_ids)
            if not nombre or not apellido1 or not has_valid_id:
                st.error("Nombre, Primer Apellido y al menos una Identificación son obligatorios.")
                return None
            
            new_data = {
                "nombre": nombre,
                "apellido1": apellido1,
                "apellido2": apellido2,
                "gender": gender,
                "fecha_nacimiento": datetime.combine(fecha_nac, datetime.min.time()) if fecha_nac else None,
                "identificaciones": final_ids,
                "contact_info": final_contacts
            }
            
            # Preservar ID si existe
            if not is_new and "_id" in person_data:
                new_data["_id"] = person_data["_id"]
                new_data["patient_code"] = person_data.get("patient_code") # Mantener código existente
                
            # Limpiar estado temporal al guardar
            del st.session_state[ids_key]
            del st.session_state[contacts_key]
                
            return new_data
            
    return None

@st.dialog("Gestión de Persona", width="large")
def person_dialog(person_id=None, on_save=None):
    """
    Modal para gestionar persona.
    Si person_id es None, es creación.
    on_save: callback(person_id) al guardar.
    """
    # --- Gestión de Estado Sucio ---
    # Usamos una clave en session_state para saber qué ID estamos editando
    current_edit_key = "current_editing_person_id"
    
    # Si cambia el ID (o pasamos de None a otro None que implica nueva apertura), limpiamos
    # Como st.dialog mantiene el estado mientras está abierto, necesitamos saber si es una "nueva apertura".
    # Una forma es verificar si las claves del formulario existen y si coinciden con lo esperado.
    # Pero st.dialog se monta y desmonta.
    
    # Estrategia: Usar un prefijo único para el formulario basado en el ID (o 'new') y un timestamp/random si es new?
    # No, mejor limpiar explícitamente si detectamos cambio.
    
    target_id = person_id or "new"
    if st.session_state.get(current_edit_key) != target_id:
        # Limpiar claves antiguas
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith("person_form_")]
        for k in keys_to_clear:
            del st.session_state[k]
        st.session_state[current_edit_key] = target_id
        
    repo = get_people_repository()
    person_data = None
    if person_id:
        person_data = repo.get_by_id(person_id)
        if not person_data:
            st.error("Persona no encontrada")
            return

    st.caption("Gestión centralizada de datos personales.")
    
    result = render_person_form(person_data)
    
    if result:
        try:
            if person_id:
                repo.update_person(person_id, result)
                st.success("Persona actualizada correctamente")
                saved_id = person_id
            else:
                # Generar patient_code si es nuevo
                # Usamos la primera identificación válida para generar el código
                first_id = next((i for i in result['identificaciones'] if i.get('value')), {})
                code = generar_codigo_paciente(
                    result['nombre'], 
                    result['apellido1'], 
                    result['apellido2'], 
                    None, # num_ss legacy (ya no lo usamos separado)
                    first_id.get('value', '0000')
                )
                
                # Verificar unicidad simple (el servicio lo hace mejor con retries, aquí hacemos un básico)
                # Si existe, añadimos sufijo aleatorio
                existing = repo.collection.find_one({"patient_code": code})
                if existing:
                    import random
                    code = f"{code[:3]}{random.randint(0, 99):02d}"
                
                result['patient_code'] = code
                result['activo'] = True
                
                saved_id = repo.create_person(result)
                st.success(f"Persona creada correctamente (Código: {code})")
            
            if on_save:
                on_save(saved_id)
            
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}")
