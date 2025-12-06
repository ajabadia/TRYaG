import streamlit as st
import time
from datetime import datetime, timedelta
from db.repositories.patient_flow import get_patient_flow_repository
from db.repositories.people import get_people_repository
from db.repositories.config import get_config_repository

def calculate_wait_time(patients_in_queue):
    """
    Calcula un tiempo de espera estimado simple.
    En un sistema real, esto usaría un modelo ML o medias históricas.
    Aquí simulamos o hacemos media simple.
    """
    if not patients_in_queue:
        return 0
    
    # Simulación: 15 min base + 5 min por paciente delante
    return 15 + (len(patients_in_queue) * 5)

def render_public_board():
    """
    Renderiza la pantalla pública de sala de espera.
    Diseño de alto contraste, fuentes grandes.
    """
    # Auto-refresh cada 30 segundos
    st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

    # Ocultar sidebar y elementos decorativos
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {display: none;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                max_width: 100%;
            }
            .big-text {
                font-size: 3rem;
                font-weight: bold;
                color: #FFF;
            }
            .status-card {
                background-color: #333;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                color: white;
                border-left: 10px solid #28a745;
            }
            .status-header {
                font-size: 1.5rem;
                color: #aaa;
                margin-bottom: 10px;
            }
            .patient-code {
                font-size: 4rem;
                font-weight: bold;
                font-family: monospace;
            }
            .room-name {
                color: #17a2b8;
                font-weight: bold;
            }
            .wait-time {
                font-size: 2rem;
                color: #ffc107;
            }
        </style>
    """, unsafe_allow_html=True)

    # Parámetros
    params = st.query_params
    room_id_filter = params.get("room_id")
    mode = params.get("mode", "room") # 'room' or 'internal'

    # Repositorios
    flow_repo = get_patient_flow_repository()
    people_repo = get_people_repository()
    config_repo = get_config_repository()

    # Título
    st.markdown(f"<h1 style='text-align: center;'>🏥 ESTADO DE URGENCIAS - {datetime.now().strftime('%H:%M')}</h1>", unsafe_allow_html=True)
    
    if mode == "internal":
        render_internal_overview(flow_repo, config_repo)
    else:
        render_room_view(room_id_filter, flow_repo, people_repo, config_repo)

def render_room_view(room_id, flow_repo, people_repo, config_repo):
    # Obtener todas las salas si no se especifica
    rooms = config_repo.get_rooms()
    
    # Filtrar pacientes
    active_flows = flow_repo.get_active_flows()
    
    # Si hay filtro de sala
    target_room_name = "Sala de Espera General"
    
    # Filtrar solo pacientes en espera
    waiting_patients = [f for f in active_flows if f.get('estado') in ['EN_ESPERA_TRIAJE', 'EN_ADMISION', 'DERIVADO']]
    
    if room_id:
        waiting_patients = [f for f in waiting_patients if f.get('sala_actual') == room_id]
        # Buscar nombre sala
        r = next((r for r in rooms if str(r['_id']) == room_id), None)
        if r: target_room_name = r['name']

    # Estimar tiempo
    wait_time = calculate_wait_time(waiting_patients)

    st.markdown(f"<h2 style='text-align: center; color: #17a2b8;'>📍 {target_room_name}</h2>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### 📋 Turno Actual")
        if not waiting_patients:
            st.info("No hay pacientes en espera en esta sala.")
        else:
            # Mostrar los 5 primeros
            for i, p_flow in enumerate(waiting_patients[:5]):
                # Anonimizar: Iniciales + ultimos 3 chars del ID
                # Necesitamos buscar datos persona
                # Nota: Hacer esto en bucle es ineficiente, pero para piloto OK.
                person = people_repo.get_by_patient_code(p_flow['patient_code'])
                display_code = p_flow['patient_code'] # Fallback
                if person:
                    initials = f"{person['nombre'][0]}{person['apellido1'][0]}"
                    suffix = person['identification_number'][-3:] if person.get('identification_number') else "000"
                    display_code = f"{initials}-{suffix}"
                
                # Color borde: Primeros Verde, Resto Gris
                border_color = "#28a745" if i == 0 else "#6c757d"
                
                st.markdown(f"""
                    <div class="status-card" style="border-left-color: {border_color};">
                        <div class="status-header">#{i+1} - {p_flow['estado']}</div>
                        <div class="patient-code">{display_code}</div>
                        <div>Espere su llamada...</div>
                    </div>
                """, unsafe_allow_html=True)

    with c2:
        st.markdown("### ⏱️ Tiempo Estimado")
        st.markdown(f"""
            <div style="background:#222; padding:30px; border-radius:15px; text-align:center;">
                <div style="font-size:1.5rem; color:#aaa;">Espera media</div>
                <div style="font-size:5rem; font-weight:bold; color:#ffc107;">{wait_time}'</div>
                <div style="font-size:1rem; color:#aaa;">minutos</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("ℹ️ **Nota:** Los tiempos son aproximados y dependen de la gravedad de los casos en curso.")


def render_internal_overview(flow_repo, config_repo):
    rooms = config_repo.get_rooms()
    active_flows = flow_repo.get_active_flows()
    
    # Agrupar por sala
    room_stats = {}
    for r in rooms:
        rid = str(r['_id'])
        count = len([f for f in active_flows if f.get('sala_actual') == rid])
        room_stats[rid] = {"name": r['name'], "count": count}
        
    st.markdown("### 📊 Monitor Global de Ocupación")
    
    # Grid de tarjetas
    cols = st.columns(4)
    for i, (rid, stats) in enumerate(room_stats.items()):
        with cols[i % 4]:
            st.metric(label=stats['name'], value=f"{stats['count']} Pacientes")

