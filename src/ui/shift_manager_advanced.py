# path: src/ui/shift_manager_advanced.py
# Creado: 2025-11-26
"""
Gestión Avanzada de Turnos con funcionalidades extendidas.
Incluye drag & drop, validación de conflictos, y estadísticas.
"""
import streamlit as st
from datetime import datetime, timedelta, date, time
from db.repositories.turnos import get_turnos_repository
from db.repositories.users import get_users_repository
from db.repositories.salas import get_all_salas
from services.staff_assignment_service import validate_shift_assignment
from db.models import Turno

def render_advanced_shift_manager():
    """
    Renderiza el gestor avanzado de turnos con funcionalidades extendidas.
    """
    st.markdown("### 📅 Gestión Avanzada de Turnos")
    
    tabs = st.tabs([
        "📋 Planificación",
        "📊 Estadísticas",
        "⚠️ Conflictos",
        "📤 Exportar"
    ])
    
    with tabs[0]:
        render_planning_tab()
    
    with tabs[1]:
        render_statistics_tab()
    
    with tabs[2]:
        render_conflicts_tab()
    
    with tabs[3]:
        render_export_tab()


def render_planning_tab():
    """
    Tab de planificación con vista mensual y creación rápida.
    """
    st.subheader("Planificación de Turnos")
    
    # Selector de mes
    col_month, col_year = st.columns(2)
    with col_month:
        month = st.selectbox(
            "Mes",
            range(1, 13),
            index=datetime.now().month - 1,
            format_func=lambda x: [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ][x-1]
        )
    
    with col_year:
        year = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now().year)
    
    st.divider()
    
    # Vista de calendario mensual
    render_monthly_calendar(year, month)
    
    st.divider()
    
    # Creación rápida de turnos
    with st.expander("➕ Crear Turno Rápido", expanded=False):
        render_quick_shift_creator()


def render_monthly_calendar(year, month):
    """
    Renderiza un calendario mensual con los turnos.
    """
    import calendar
    
    # Obtener días del mes
    cal = calendar.monthcalendar(year, month)
    
    # Obtener turnos del mes
    repo = get_turnos_repository()
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Header con días de la semana
    days_of_week = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    cols = st.columns(7)
    for i, day_name in enumerate(days_of_week):
        with cols[i]:
            st.markdown(f"**{day_name}**")
    
    # Renderizar semanas
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("")  # Día vacío
                else:
                    current_date = date(year, month, day)
                    shifts_count = len(repo.get_active_shifts(datetime.combine(current_date, datetime.min.time())))
                    
                    # Estilo según si es hoy, fin de semana, etc.
                    is_today = current_date == date.today()
                    is_weekend = i >= 5
                    
                    bg_color = "#e3f2fd" if is_today else ("#f5f5f5" if is_weekend else "white")
                    border_color = "#2196f3" if is_today else "#ddd"
                    
                    st.markdown(
                        f"""
                        <div style="
                            background-color: {bg_color};
                            border: 2px solid {border_color};
                            border-radius: 8px;
                            padding: 8px;
                            min-height: 60px;
                            text-align: center;">
                            <div style="font-weight: bold; font-size: 16px;">{day}</div>
                            <div style="font-size: 12px; color: #666; margin-top: 4px;">
                                {shifts_count} turno{'s' if shifts_count != 1 else ''}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


def render_quick_shift_creator():
    """
    Formulario rápido para crear turnos.
    """
    users_repo = get_users_repository()
    all_users = users_repo.get_all_users(active_only=True)
    salas = get_all_salas()
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_options = {str(u['_id']): (u.get('nombre_completo') or f"{u.get('nombre', '')} {u.get('apellidos', '')}".strip() or u.get('username', 'Usuario')) for u in all_users}
        selected_user = st.selectbox(
            "Usuario",
            options=list(user_options.keys()),
            format_func=lambda x: user_options[x],
            key="quick_shift_user"
        )
        
        fecha_desde = st.date_input("Fecha Desde", value=date.today())
        horario_inicio = st.time_input("Hora Inicio", value=time(8, 0))
    
    with col2:
        sala_options = {s['codigo']: f"{s['nombre']} ({s['codigo']})" for s in salas}
        selected_sala = st.selectbox(
            "Sala",
            options=list(sala_options.keys()),
            format_func=lambda x: sala_options[x],
            key="quick_shift_sala"
        )
        
        fecha_hasta = st.date_input("Fecha Hasta", value=date.today())
        horario_fin = st.time_input("Hora Fin", value=time(15, 0))
    
    if st.button("✅ Crear Turno", type="primary", use_container_width=True):
        # Validar
        valid, message = validate_shift_assignment(
            selected_user,
            selected_sala,
            fecha_desde,
            horario_inicio,
            horario_fin
        )
        
        if not valid:
            st.error(f"❌ {message}")
        else:
            # Crear turno
            repo = get_turnos_repository()
            turno = Turno(
                user_id=selected_user,
                sala_code=selected_sala,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                horario_inicio=horario_inicio,
                horario_fin=horario_fin,
                activo=True
            )
            
            repo.create(turno)
            st.success("✅ Turno creado correctamente")
            
            if message:
                st.warning(message)
            
            st.rerun()


def render_statistics_tab():
    """
    Tab de estadísticas de cobertura y distribución.
    """
    st.subheader("Estadísticas de Turnos")
    
    # Período de análisis
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=date.today() - timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Hasta", value=date.today())
    
    st.divider()
    
    # Métricas generales
    repo = get_turnos_repository()
    users_repo = get_users_repository()
    
    # Calcular estadísticas
    total_shifts = 0
    shifts_by_sala = {}
    shifts_by_user = {}
    
    # Iterar por cada día del período
    current_date = fecha_inicio
    while current_date <= fecha_fin:
        day_shifts = repo.get_active_shifts(datetime.combine(current_date, datetime.min.time()))
        total_shifts += len(day_shifts)
        
        for shift in day_shifts:
            # Por sala
            sala = shift.sala_code
            shifts_by_sala[sala] = shifts_by_sala.get(sala, 0) + 1
            
            # Por usuario
            user_id = shift.user_id
            shifts_by_user[user_id] = shifts_by_user.get(user_id, 0) + 1
        
        current_date += timedelta(days=1)
    
    # Mostrar métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Turnos", total_shifts)
    with col2:
        st.metric("Salas Cubiertas", len(shifts_by_sala))
    with col3:
        avg_per_day = total_shifts / max((fecha_fin - fecha_inicio).days, 1)
        st.metric("Promedio/Día", f"{avg_per_day:.1f}")
    
    st.divider()
    
    # Gráficos
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### Turnos por Sala")
        if shifts_by_sala:
            import pandas as pd
            df_salas = pd.DataFrame(list(shifts_by_sala.items()), columns=['Sala', 'Turnos'])
            st.bar_chart(df_salas.set_index('Sala'))
        else:
            st.info("No hay datos para mostrar")
    
    with col_chart2:
        st.markdown("#### Turnos por Usuario")
        if shifts_by_user:
            import pandas as pd
            # Obtener nombres de usuarios
            user_names = {}
            for user_id in shifts_by_user.keys():
                user = users_repo.get_by_id(user_id)
                if user:
                    user_names[user_id] = user.get('nombre_completo', user_id)
            
            df_users = pd.DataFrame([
                {'Usuario': user_names.get(uid, uid), 'Turnos': count}
                for uid, count in shifts_by_user.items()
            ])
            st.bar_chart(df_users.set_index('Usuario'))
        else:
            st.info("No hay datos para mostrar")


def render_conflicts_tab():
    """
    Tab de detección y resolución de conflictos.
    """
    st.subheader("Detección de Conflictos")
    
    from services.staff_assignment_service import get_assignment_conflicts_report
    
    conflicts = get_assignment_conflicts_report()
    
    if not conflicts:
        st.success("✅ No se detectaron conflictos de turnos")
    else:
        st.warning(f"⚠️ Se detectaron {len(conflicts)} conflictos")
        
        for conflict in conflicts:
            nombre_conflict = conflict.get('nombre_completo') or f"{conflict.get('nombre', '')} {conflict.get('apellidos', '')}".strip() or conflict.get('username', 'Usuario')
            with st.expander(f"⚠️ {nombre_conflict}", expanded=False):
                st.markdown(f"""
                **Usuario:** {nombre_conflict}  
                **Asignación Fija:** {conflict['fixed_sala']}  
                **Turno Temporal:** {conflict['shift_sala']}  
                **Horario:** {conflict['horario']}  
                **Fecha:** {conflict['fecha'].strftime('%d/%m/%Y')}
                """)


def render_export_tab():
    """
    Tab de exportación de planificación.
    """
    st.subheader("Exportar Planificación")
    
    # Opciones de exportación
    export_format = st.radio(
        "Formato",
        ["Excel", "PDF", "CSV"],
        horizontal=True
    )
    
    # Período
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=date.today(), key="export_from")
    with col2:
        fecha_fin = st.date_input("Hasta", value=date.today() + timedelta(days=30), key="export_to")
    
    if st.button("📤 Exportar", type="primary", use_container_width=True):
        if export_format == "Excel":
            data = _generate_excel_export(fecha_inicio, fecha_fin)
            st.download_button(
                "⬇️ Descargar Excel",
                data=data,
                file_name=f"turnos_{fecha_inicio}_{fecha_fin}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif export_format == "CSV":
            data = _generate_csv_export(fecha_inicio, fecha_fin)
            st.download_button(
                "⬇️ Descargar CSV",
                data=data,
                file_name=f"turnos_{fecha_inicio}_{fecha_fin}.csv",
                mime="text/csv"
            )
        else:
            st.info("Exportación a PDF en desarrollo")


def _generate_excel_export(fecha_inicio, fecha_fin):
    """Genera archivo Excel con la planificación."""
    import pandas as pd
    from io import BytesIO
    
    repo = get_turnos_repository()
    users_repo = get_users_repository()
    
    # Recopilar datos
    data = []
    current_date = fecha_inicio
    while current_date <= fecha_fin:
        day_shifts = repo.get_active_shifts(datetime.combine(current_date, datetime.min.time()))
        
        for shift in day_shifts:
            user = users_repo.get_by_id(shift.user_id)
            data.append({
                'Fecha': current_date,
                'Usuario': user.get('nombre_completo') if user else shift.user_id,
                'Sala': shift.sala_code,
                'Hora Inicio': shift.horario_inicio,
                'Hora Fin': shift.horario_fin
            })
        
        current_date += timedelta(days=1)
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Turnos', index=False)
    
    output.seek(0)
    return output.read()


def _generate_csv_export(fecha_inicio, fecha_fin):
    """Genera archivo CSV con la planificación."""
    import pandas as pd
    
    repo = get_turnos_repository()
    users_repo = get_users_repository()
    
    data = []
    current_date = fecha_inicio
    while current_date <= fecha_fin:
        day_shifts = repo.get_active_shifts(datetime.combine(current_date, datetime.min.time()))
        
        for shift in day_shifts:
            user = users_repo.get_by_id(shift.user_id)
            data.append({
                'Fecha': current_date,
                'Usuario': user.get('nombre_completo') if user else shift.user_id,
                'Sala': shift.sala_code,
                'Hora Inicio': shift.horario_inicio,
                'Hora Fin': shift.horario_fin
            })
        
        current_date += timedelta(days=1)
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')
