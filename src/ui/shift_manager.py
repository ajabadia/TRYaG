import streamlit as st
from datetime import datetime, timedelta, date, time
from db.repositories.turnos import get_turnos_repository
from db.repositories.users import get_users_repository
from db.repositories.salas import get_all_salas
from db.models import Turno

def render_shift_manager():
    st.markdown("### 📅 Gestión de Turnos (Temporal)")
    st.markdown("Planifica los turnos de trabajo por fecha y hora.")
    
    tab_list, tab_calendar, tab_create = st.tabs(["📋 Listado de Turnos", "📅 Calendario Semanal", "➕ Nuevo Turno"])
    
    repo = get_turnos_repository()
    users_repo = get_users_repository()
    
    # -----------------------------------------------------------------------
    # Tab: Listado (Existing)
    # -----------------------------------------------------------------------
    with tab_list:
        st.subheader("Turnos Activos")
        # ... (existing code for list) ...

    # -----------------------------------------------------------------------
    # Tab: Calendario Semanal (NEW)
    # -----------------------------------------------------------------------
    with tab_calendar:
        st.subheader("Vista Semanal")
        
        # Selector de semana (por defecto hoy)
        col_nav1, col_nav2 = st.columns([1, 4])
        with col_nav1:
            ref_date = st.date_input("Semana de referencia", value=date.today(), key="cal_ref_date")
        
        # Calcular inicio (Lunes) y fin (Domingo) de la semana
        start_of_week = ref_date - timedelta(days=ref_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        st.caption(f"Mostrando semana del **{start_of_week.strftime('%d/%m')}** al **{end_of_week.strftime('%d/%m')}**")
        st.divider()
        
        # Crear columnas para los 7 días
        days_cols = st.columns(7)
        days_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        
        # Obtener todos los turnos activos en este rango
        # Nota: get_active_shifts busca por un día específico. 
        # Para eficiencia, idealmente el repo debería tener un método get_shifts_in_range.
        # Por ahora, iteraremos por día.
        
        for i, day_col in enumerate(days_cols):
            current_day = start_of_week + timedelta(days=i)
            
            with day_col:
                # Header del día
                st.markdown(f"<div style='text-align: center; font-weight: bold; border-bottom: 2px solid #ddd; margin-bottom: 10px;'>{days_names[i]}<br><span style='font-size: 0.8em; color: #666;'>{current_day.strftime('%d/%m')}</span></div>", unsafe_allow_html=True)
                
                # Buscar turnos para este día
                # Usamos datetime.combine para tener un datetime completo para la query
                day_shifts = repo.get_active_shifts(datetime.combine(current_day, datetime.min.time()))
                
                if not day_shifts:
                    st.markdown("<div style='text-align: center; color: #ccc; font-size: 0.8em;'>-</div>", unsafe_allow_html=True)
                else:
                    for shift in day_shifts:
                        # Obtener nombre usuario (cachear si es posible en futuro)
                        u = users_repo.get_by_id(shift.user_id)
                        nombre_completo = u.get('nombre_completo') or f"{u.get('nombre', '')} {u.get('apellidos', '')}".strip() or u.get('username', 'Usuario')
                        u_name = nombre_completo.split()[0] if u else "???" # Solo primer nombre para ahorrar espacio
                        
                        # Color distintivo por sala (hash simple o lógica)
                        # Por simplicidad: borde coloreado
                        
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #f0f2f6;
                                border-left: 4px solid #28a745;
                                padding: 4px;
                                margin-bottom: 6px;
                                border-radius: 4px;
                                font-size: 0.75rem;
                                overflow: hidden;
                            ">
                                <strong>{shift.horario_inicio}-{shift.horario_fin}</strong><br>
                                {u_name}<br>
                                <span style="color: #666;">{shift.sala_code}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    # -----------------------------------------------------------------------
    # Tab: Nuevo Turno (Existing)
    # -----------------------------------------------------------------------
    with tab_create:
        st.subheader("Turnos Activos")
        # Filtro por fecha
        selected_date = st.date_input("Filtrar por fecha", value=date.today())
        
        turnos = repo.get_active_shifts(datetime.combine(selected_date, datetime.min.time()))
        
        if not turnos:
            st.info("No hay turnos programados para esta fecha.")
        else:
            for turno in turnos:
                with st.expander(f"{turno.sala_code} - {turno.horario_inicio} a {turno.horario_fin}"):
                    # Buscar nombre de usuario
                    user = users_repo.get_by_id(turno.user_id)
                    user_name = (user.get('nombre_completo') or f"{user.get('nombre', '')} {user.get('apellidos', '')}".strip() or user.get('username', 'Usuario')) if user else "Desconocido"
                    
                    st.write(f"**Usuario:** {user_name}")
                    st.write(f"**Notas:** {turno.notas}")
                    st.write(f"**Vigencia:** {turno.fecha_desde.date()} al {turno.fecha_hasta.date()}")

    with tab_create:
        st.subheader("Asignar Nuevo Turno")
        
        # Select User
        users = users_repo.get_all_users()
        if not users:
             st.warning("No hay usuarios creados. Vaya a Configuración > Usuarios para crear uno.")
        else:
            user_options = {str(u['_id']): f"{u.get('nombre_completo', 'Sin Nombre')} ({u.get('rol', 'N/A')})" for u in users}
            selected_user_id = st.selectbox("Usuario", options=list(user_options.keys()), format_func=lambda x: user_options[x])
            
            # Select Room - Filter out waiting rooms
            salas = get_all_salas()
            
            # Filter logic: Exclude rooms where subtipo is 'espera'
            # We assume 'subtipo' key exists, defaulting to empty string if not found
            # Normalize comparison to handle potential case/accent differences if needed, though 'espera' is standard.
            selectable_salas = [s for s in salas if s.get('subtipo', '').lower() != 'espera']
            
            if not salas:
                st.warning("⚠️ No se encontraron salas en el sistema. Vaya a 'Gestión de Salas' para crear una.")
            elif not selectable_salas:
                st.warning("⚠️ No hay salas de atención disponibles.")
                st.info("ℹ️ Todas las salas existentes están marcadas como 'espera'. Los turnos solo se pueden asignar a salas de atención (Boxes, Consultas, Triaje).")
                
                # Debug info (expandable)
                with st.expander("Ver detalles de salas excluidas"):
                    for s in salas:
                        st.write(f"- **{s.get('nombre')}** ({s.get('codigo')}): Tipo='{s.get('tipo')}', Subtipo='{s.get('subtipo')}'")
            else:
                sala_options = {s['codigo']: f"{s.get('nombre', s['codigo'])} ({s['codigo']})" for s in selectable_salas}
                selected_sala = st.selectbox("Sala", options=list(sala_options.keys()), format_func=lambda x: sala_options[x])
                
                col1, col2 = st.columns(2)
                with col1:
                    f_desde = st.date_input("Fecha Desde", value=date.today())
                    h_inicio = st.time_input("Hora Inicio", value=time(8, 0))
                with col2:
                    f_hasta = st.date_input("Fecha Hasta", value=date.today())
                    h_fin = st.time_input("Hora Fin", value=time(15, 0))
                    
                notas = st.text_area("Notas")
                
                if st.button("Crear Turno"):
                    # Validation: End date must be >= Start date
                    if f_hasta < f_desde:
                        st.error("La fecha de fin no puede ser anterior a la fecha de inicio.")
                        st.stop()
                        
                    # Validation: End time must be > Start time
                    if h_fin <= h_inicio:
                        st.error("La hora de fin debe ser posterior a la hora de inicio.")
                        st.stop()

                    # Validation: Overlap Check
                    user_shifts = repo.get_by_user(selected_user_id)
                    has_conflict = False
                    conflict_details = ""
                    
                    new_start_dt = datetime.combine(f_desde, datetime.min.time())
                    new_end_dt = datetime.combine(f_hasta, datetime.min.time())
                    
                    for shift in user_shifts:
                        # Check Date Overlap
                        # Logic: max(start1, start2) <= min(end1, end2)
                        overlap_start = max(new_start_dt, shift.fecha_desde)
                        overlap_end = min(new_end_dt, shift.fecha_hasta)
                        
                        if overlap_start <= overlap_end:
                            # Dates overlap, now check Time Overlap
                            # Convert string times to time objects for comparison
                            shift_start_time = datetime.strptime(shift.horario_inicio, "%H:%M").time()
                            shift_end_time = datetime.strptime(shift.horario_fin, "%H:%M").time()
                            
                            # Logic: max(start1, start2) < min(end1, end2)
                            # Note: Using < for strict overlap (touching is usually allowed, but let's be safe)
                            time_overlap_start = max(h_inicio, shift_start_time)
                            time_overlap_end = min(h_fin, shift_end_time)
                            
                            if time_overlap_start < time_overlap_end:
                                has_conflict = True
                                conflict_details = f"Conflicto con turno en sala {shift.sala_code} ({shift.fecha_desde.date()} - {shift.fecha_hasta.date()}, {shift.horario_inicio}-{shift.horario_fin})"
                                break
                    
                    if has_conflict:
                        st.error(f"❌ No se puede asignar el turno: {conflict_details}")
                    else:
                        new_turno = Turno(
                            user_id=selected_user_id,
                            sala_code=selected_sala,
                            fecha_desde=new_start_dt,
                            fecha_hasta=new_end_dt,
                            horario_inicio=h_inicio.strftime("%H:%M"),
                            horario_fin=h_fin.strftime("%H:%M"),
                            notas=notas
                        )
                        repo.create(new_turno)
                        
                        # Send Notification
                        from services.notification_service import notify_shift_created
                        user_data = users_repo.get_by_id(selected_user_id)
                        user_name = user_data.get('nombre_completo', 'Usuario') if user_data else "Usuario"
                        
                        notify_shift_created(
                            user_name=user_name,
                            sala_code=selected_sala,
                            fecha_desde=new_start_dt,
                            fecha_hasta=new_end_dt,
                            horario=f"{h_inicio.strftime('%H:%M')} - {h_fin.strftime('%H:%M')}"
                        )
                        
                        st.success("Turno creado correctamente")
                        st.rerun()
