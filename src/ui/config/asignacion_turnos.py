# path: src/ui/config/asignacion_turnos.py
# Creado: 2025-11-26
"""
UI para la asignación de personal a salas (Gestión de Turnos).
Permite asignar usuarios activos a las salas disponibles del centro.
"""
import streamlit as st
from db.repositories.users import get_users_repository
from db.repositories.funciones import get_funcion_by_code

def render_asignacion_turnos(salas: list):
    """
    Renderiza la interfaz de asignación de turnos.
    
    Args:
        salas: Lista de diccionarios con la configuración de las salas.
    """
    st.markdown("### 📍 Asignación de Salas (Fija)")
    st.markdown("Asigna médicos, enfermeros y personal administrativo a su sala habitual.")
    
    if not salas:
        st.warning("No hay salas configuradas. Ve a 'Gestión de Salas' para crear alguna.")
        return

    # Deduplicar salas por código para evitar errores de claves duplicadas
    unique_salas = {}
    for s in salas:
        if s.get('codigo'):
            unique_salas[s['codigo']] = s
    salas = list(unique_salas.values())

    users_repo = get_users_repository()
    all_users = users_repo.get_all_users(active_only=True)
    
    if not all_users:
        st.warning("No hay usuarios activos en el sistema.")
        return

    # Organizar usuarios por función para facilitar la selección
    # Y crear un mapa de usuario_id -> usuario para acceso rápido
    users_map = {str(u["_id"]): u for u in all_users}
    
    # Mapa inverso: Sala -> Lista de IDs de usuarios asignados
    # Calculado en tiempo real basado en el campo 'sala_asignada' de los usuarios
    room_assignments = {sala["codigo"]: [] for sala in salas}
    
    # Usuarios sin asignar (para mostrar en un pool si fuera necesario, o solo filtrar)
    unassigned_users = []
    
    for u in all_users:
        sala_code = u.get("sala_asignada")
        if sala_code and sala_code in room_assignments:
            room_assignments[sala_code].append(str(u["_id"]))
        else:
            unassigned_users.append(u)

    # -----------------------------------------------------------------------
    # Grid de Salas
    # -----------------------------------------------------------------------
    
    # Filtrar salas por tipo para organizar mejor visualmente
    tipos_sala = sorted(list(set(s.get("tipo", "otros") for s in salas)))
    
    selected_type = st.selectbox("Filtrar por Tipo de Sala", ["Todos"] + tipos_sala)
    
    salas_to_show = salas
    if selected_type != "Todos":
        salas_to_show = [s for s in salas if s.get("tipo") == selected_type]

    for sala in salas_to_show:
        sala_code = sala.get("codigo")
        sala_nombre = sala.get("nombre")
        
        with st.expander(f"📍 {sala_nombre} ({sala_code})", expanded=True):
            current_assigned_ids = room_assignments.get(sala_code, [])
            
            # Formulario para esta sala
            with st.form(key=f"form_turnos_{sala_code}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Multiselect con todos los usuarios
                    # Marcamos como default los que ya están en esta sala
                    options = list(users_map.keys())
                    
                    # Función para formatear la etiqueta del usuario en el select
                    def format_user_label(uid):
                        u = users_map[uid]
                        funcs = u.get("funciones", [])
                        main_func = funcs[0] if funcs else "Sin función"
                        # Indicador si ya está en OTRA sala (para avisar)
                        current_sala = u.get("sala_asignada")
                        extra_info = ""
                        if current_sala and current_sala != sala_code:
                            extra_info = f" (Actualmente en {current_sala})"
                        
                        nombre = u.get('nombre_completo') or f"{u.get('nombre', '')} {u.get('apellidos', '')}".strip() or u.get('username', 'Usuario')
                        return f"{nombre} - {main_func.capitalize()}{extra_info}"

                    selected_ids = st.multiselect(
                        "Personal Asignado",
                        options=options,
                        default=current_assigned_ids,
                        format_func=format_user_label,
                        help="Selecciona los usuarios que trabajarán en esta sala."
                    )
                
                with col2:
                    st.write("") # Spacer
                    st.write("") # Spacer
                    if st.form_submit_button("💾 Actualizar Asignación"):
                        _update_assignments(users_repo, sala_code, current_assigned_ids, selected_ids, users_map)
                        st.rerun()

def _update_assignments(repo, sala_code, old_ids, new_ids, users_map):
    """
    Actualiza la base de datos con las nuevas asignaciones.
    
    Args:
        repo: UsersRepository
        sala_code: Código de la sala actual
        old_ids: Lista de IDs que estaban asignados antes
        new_ids: Lista de IDs seleccionados ahora
    """
    # 1. Identificar usuarios a desasignar (estaban antes, no están ahora)
    to_remove = set(old_ids) - set(new_ids)
    for uid in to_remove:
        repo.update_user(uid, {"sala_asignada": None})
        
    # 2. Identificar usuarios a asignar (están ahora)
    # Nota: Esto sobrescribirá cualquier otra sala que tuvieran asignada
    for uid in new_ids:
        # Verificar si cambia de sala
        user = users_map[uid]
        if user.get("sala_asignada") != sala_code:
            repo.update_user(uid, {"sala_asignada": sala_code})
            
    st.toast(f"Asignaciones actualizadas para sala {sala_code}")
