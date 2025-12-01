# path: src/ui/config/staff_conflicts_viewer.py
# Creado: 2025-11-26
"""
Visor de conflictos entre asignaciones fijas y turnos temporales.
"""
import streamlit as st
from datetime import date, datetime
from services.staff_assignment_service import (
    get_assignment_conflicts_report,
    get_user_assignment_info
)
from db.repositories.users import get_users_repository

def render_staff_conflicts_viewer():
    """
    Renderiza el visor de conflictos entre asignaciones fijas y turnos.
    """
    st.markdown("### ⚠️ Conflictos de Asignación: Fija vs Turnos")
    st.markdown("""
    Esta vista muestra los casos donde un usuario tiene una **asignación fija** a una sala,
    pero tiene **turnos temporales** en otras salas para hoy.
    
    **Regla de Prioridad:** Los turnos temporales siempre prevalecen sobre la asignación fija.
    """)
    
    st.divider()
    
    # Obtener reporte de conflictos
    conflicts = get_assignment_conflicts_report()
    
    if not conflicts:
        st.success("✅ No hay conflictos detectados para hoy.")
        st.info("Todos los usuarios están asignados consistentemente.")
        return
    
    # Mostrar estadísticas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Conflictos Detectados", len(conflicts))
    with col2:
        unique_users = len(set(c['user_id'] for c in conflicts))
        st.metric("Usuarios Afectados", unique_users)
    
    st.divider()
    
    # Tabla de conflictos
    st.markdown("#### Detalle de Conflictos")
    
    for conflict in conflicts:
        nombre_conflict = conflict.get('nombre_completo') or f"{conflict.get('nombre', '')} {conflict.get('apellidos', '')}".strip() or conflict.get('username', 'Usuario')
        with st.expander(f"⚠️ {nombre_conflict}", expanded=False):
            col_info, col_action = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"""
                **Usuario:** {nombre_conflict}  
                **Asignación Fija:** `{conflict['fixed_sala']}`  
                **Turno Temporal:** `{conflict['shift_sala']}`  
                **Horario:** {conflict['horario']}  
                **Fecha:** {conflict['fecha'].strftime('%d/%m/%Y')}
                """)
                
                st.info(f"""
                💡 **Resolución Automática:**  
                Durante el horario {conflict['horario']}, el usuario estará en **{conflict['shift_sala']}** (turno).  
                Fuera de ese horario, estará en **{conflict['fixed_sala']}** (asignación fija).
                """)
            
            with col_action:
                if st.button("Ver Detalles", key=f"details_{conflict['user_id']}"):
                    st.session_state[f"show_details_{conflict['user_id']}"] = True
                    st.rerun()
            
            # Mostrar detalles si se solicitó
            if st.session_state.get(f"show_details_{conflict['user_id']}", False):
                st.divider()
                st.markdown("##### Información Completa de Asignación")
                
                info = get_user_assignment_info(conflict['user_id'])
                
                st.json({
                    "Asignación Fija": info['fixed_assignment'],
                    "Turno Actual": info['current_shift'],
                    "Sala Efectiva Ahora": info['current_sala'],
                    "Tipo de Asignación": info['assignment_type'],
                    "Todos los Turnos Hoy": info['all_shifts_today']
                })
                
                if st.button("Cerrar Detalles", key=f"close_{conflict['user_id']}"):
                    st.session_state[f"show_details_{conflict['user_id']}"] = False
                    st.rerun()
    
    st.divider()
    
    # Recomendaciones
    st.markdown("#### 💡 Recomendaciones")
    st.markdown("""
    - **No es necesario tomar acción:** El sistema gestiona automáticamente la prioridad.
    - **Turnos temporales** siempre prevalecen durante su horario.
    - **Asignación fija** se usa cuando no hay turno activo.
    - Si deseas evitar estos conflictos, considera:
      1. Eliminar la asignación fija cuando uses turnos exclusivamente.
      2. O asegurar que los turnos sean en la misma sala que la asignación fija.
    """)


def render_user_assignment_timeline():
    """
    Renderiza una línea de tiempo de asignaciones para un usuario específico.
    """
    st.markdown("### 📅 Línea de Tiempo de Asignación")
    
    users_repo = get_users_repository()
    all_users = users_repo.get_all_users(active_only=True)
    
    if not all_users:
        st.warning("No hay usuarios activos.")
        return
    
    # Selector de usuario
    user_options = {str(u['_id']): (u.get('nombre_completo') or f"{u.get('nombre', '')} {u.get('apellidos', '')}".strip() or u.get('username', 'Usuario')) for u in all_users}
    selected_user_id = st.selectbox(
        "Seleccionar Usuario",
        options=list(user_options.keys()),
        format_func=lambda x: user_options[x]
    )
    
    if not selected_user_id:
        return
    
    # Selector de fecha
    selected_date = st.date_input("Fecha", value=date.today())
    
    st.divider()
    
    # Obtener información de asignación para diferentes horas del día
    hours = range(0, 24)
    timeline_data = []
    
    for hour in hours:
        ref_datetime = datetime.combine(selected_date, datetime.min.time().replace(hour=hour))
        info = get_user_assignment_info(selected_user_id, ref_datetime)
        
        timeline_data.append({
            "hora": f"{hour:02d}:00",
            "sala": info['current_sala'] or "Sin asignar",
            "tipo": info['assignment_type']
        })
    
    # Visualizar timeline
    st.markdown("#### Asignación por Hora")
    
    for data in timeline_data:
        tipo_icon = "🕐" if data['tipo'] == "turno" else ("📌" if data['tipo'] == "fija" else "⚪")
        color = "#28a745" if data['tipo'] == "turno" else ("#007bff" if data['tipo'] == "fija" else "#6c757d")
        
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 4px 8px;
                margin-bottom: 2px;
                border-left: 4px solid {color};
                background-color: rgba(0,0,0,0.02);">
                <span style="font-weight: bold; width: 60px;">{data['hora']}</span>
                <span>{tipo_icon}</span>
                <span>{data['sala']}</span>
                <span style="color: #666; font-size: 0.8em;">({data['tipo']})</span>
            </div>
            """,
            unsafe_allow_html=True
        )
