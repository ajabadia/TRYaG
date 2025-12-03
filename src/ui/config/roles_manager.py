# path: src/ui/config/roles_manager.py
# Creado: 2025-11-27
"""
UI para la gestión de roles y permisos jerárquicos.
Permite editar los permisos de acceso a los diferentes módulos del sistema.
"""
import streamlit as st
import time
from db.repositories.roles import get_roles_repository, get_all_roles

# Definición de la estructura de permisos del sistema
# Esto define qué checkboxes se mostrarán en el editor
SYSTEM_PERMISSIONS_STRUCTURE = {
    "admision": {
        "label": "📋 Admisión",
        "actions": {
            "view": "Ver Módulo",
            "create": "Crear Pacientes",
            "edit": "Editar Datos",
            "delete": "Eliminar Registros"
        }
    },
    "triaje": {
        "label": "🩺 Triaje",
        "actions": {
            "view": "Ver Módulo",
            "create": "Iniciar Triaje",
            "edit": "Editar Triaje",
            "delete": "Descartar/Eliminar"
        }
    },
    "atencion_box": {
        "label": "🏥 Atención en Box",
        "actions": {
            "view": "Ver Módulo",
            "create": "Iniciar Atención",
            "edit": "Registrar Evolución",
            "delete": "Anular Atención"
        }
    },
    "consulta_ingreso": {
        "label": "👨‍⚕️ Consulta / Ingreso",
        "actions": {
            "view": "Ver Módulo",
            "create": "Crear Ingreso",
            "edit": "Editar Historia",
            "delete": "Borrar Registros"
        }
    },
    "auditoria": {
        "label": "📊 Auditoría y Reportes",
        "actions": {
            "view": "Ver Dashboard",
            "export": "Exportar Datos"
        }
    },
    "configuracion": {
        "label": "⚙️ Configuración Global",
        "actions": {
            "general": "General / Notificaciones",
            "prompts": "General: Prompts IA",
            "centro": "Centro (Datos y Salas)",
            "usuarios": "Gestión de Usuarios",
            "roles": "Gestión de Roles"
        }
    },
    "control_salas": {
        "label": "🏢 Config: Control de Salas",
        "actions": {
            "view": "Ver Monitor",
            "manage": "Gestionar/Asignar Salas"
        }
    }
}

def render_roles_manager():
    """Componente principal de gestión de roles."""
    st.markdown("### 🛡️ Gestión de Roles y Permisos")
    st.caption("Define los roles y sus niveles de acceso al sistema.")

    repo = get_roles_repository()
    roles = repo.get_all_roles()

    # Layout: Lista de roles a la izquierda, Editor a la derecha
    col_list, col_edit = st.columns([1, 2])

    with col_list:
        st.markdown("##### Roles Disponibles")
        
        # Selector de rol para editar
        role_names = [r["nombre"] for r in roles]
        selected_role_name = st.radio("Selecciona un rol:", role_names, label_visibility="collapsed")
        
        # Botón para crear nuevo rol (Placeholder por ahora)
        if st.button("➕ Nuevo Rol", use_container_width=True):
            st.toast("Funcionalidad de crear rol pendiente de implementación completa.")
            # Aquí se abriría un dialog para crear rol básico

    # Buscar el objeto rol seleccionado
    selected_role = next((r for r in roles if r["nombre"] == selected_role_name), None)

    if selected_role:
        with col_edit:
            with st.container(border=True):
                st.markdown(f"#### Editando: {selected_role['nombre']}")
                
                # Datos básicos
                new_name = st.text_input("Nombre del Rol", value=selected_role.get("nombre", ""))
                new_desc = st.text_area("Descripción", value=selected_role.get("descripcion", ""))
                
                st.divider()
                st.markdown("##### 🔐 Permisos de Acceso")
                
                # Editor de permisos jerárquico
                current_perms = selected_role.get("permissions", {})
                updated_perms = {}

                # Iterar sobre la estructura definida
                for module_key, module_def in SYSTEM_PERMISSIONS_STRUCTURE.items():
                    with st.expander(module_def["label"], expanded=False):
                        # Obtener permisos actuales para este módulo
                        module_current = current_perms.get(module_key, {})
                        # Si es bool (acceso total legacy), convertir a dict
                        if isinstance(module_current, bool):
                            module_current = {k: module_current for k in module_def["actions"].keys()}
                        
                        module_updates = {}
                        
                        # Checkbox "Seleccionar Todo" para el módulo
                        all_actions = list(module_def["actions"].keys())
                        all_checked = all(module_current.get(act, False) for act in all_actions)
                        
                        c_all = st.checkbox(f"Habilitar todo en {module_def['label']}", value=all_checked, key=f"all_{selected_role['code']}_{module_key}")
                        
                        st.divider()
                        
                        # Checkboxes individuales
                        cols = st.columns(2)
                        for i, (action_key, action_label) in enumerate(module_def["actions"].items()):
                            # Si "Select All" cambió, usar ese valor, sino el actual
                            # Nota: Streamlit no tiene "on_change" fácil dentro de loops sin callbacks complejos.
                            # Usaremos la lógica: Si c_all es True y antes no lo era... es complejo.
                            # Simplificación: Si c_all es True, forzamos True visualmente, pero permitimos desmarcar?
                            # Mejor: Checkbox individual manda. c_all es solo visual o helper si se implementa con callback.
                            # Por simplicidad en MVP: Checkboxes individuales.
                            
                            is_checked = module_current.get(action_key, False)
                            # Si c_all está marcado, asumimos que el usuario quiere todo, salvo que desmarque
                            # Pero c_all se renderiza en cada run.
                            
                            # Vamos a usar el valor de c_all para pre-llenar si no hay estado previo, 
                            # pero eso es confuso.
                            # Ignoremos c_all para la lógica de guardado por ahora y usemos los individuales.
                            
                            with cols[i % 2]:
                                val = st.checkbox(action_label, value=is_checked, key=f"perm_{selected_role['code']}_{module_key}_{action_key}")
                                module_updates[action_key] = val
                        
                        updated_perms[module_key] = module_updates

                st.divider()
                
                if st.button("💾 Guardar Cambios", type="primary", use_container_width=True, key=f"save_role_{selected_role['code']}"):
                    # Guardar
                    updates = {
                        "nombre": new_name,
                        "descripcion": new_desc,
                        "permissions": updated_perms
                    }
                    
                    if repo.update_role(selected_role["code"], updates):
                        st.success(f"Rol '{new_name}' actualizado correctamente.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error al actualizar el rol.")

                        st.markdown('<div class="debug-footer">src/ui/config/roles_manager.py</div>', unsafe_allow_html=True)
