# path: src/components/triage/vital_signs/form.py
import streamlit as st
from components.triage.triage_logic import calculate_worst_case, calculate_news_score
from components.triage.ptr_logic import calculate_ptr_score
from .utils import get_all_configs
from .input import render_vital_sign_input

def render_vital_signs_form():
    """Renderiza el formulario completo de signos vitales."""
    st.subheader("2. Signos Vitales")
    
    # Obtener edad del paciente (Contexto)
    age = st.session_state.datos_paciente.get('edad', 40)
    
    # Cargar configuraciones una sola vez
    configs = get_all_configs(age)
    
    # CSS para Grid Responsivo
    from utils.ui_utils import load_css
    load_css("src/assets/css/components/forms.css")

    # --- SIMULACIÓN IOT ---
    import time
    import random
    from db.repositories.salas import get_sala

    # Obtener sala actual para verificar dispositivos
    sala_code = st.session_state.get("sala_seleccionada")
    devices = []
    if sala_code:
        if isinstance(sala_code, dict): sala_code = sala_code.get("codigo")
        sala = get_sala(sala_code)
        if sala: devices = sala.get("devices", [])

    # Botón de Captura (solo si hay dispositivos)
    if devices:
        col_iot, _ = st.columns([1, 3])
        with col_iot:
            if st.button("📡 Capturar Signos Vitales", help=f"Dispositivos conectados: {', '.join(devices)}"):
                with st.spinner("Conectando con dispositivos médicos..."):
                    time.sleep(random.uniform(1.5, 3.0)) # Simular delay conexión
                    
                    if "Monitor Multiparamétrico" in devices or "Pulsioxímetro" in devices:
                        if 'vital_signs' not in st.session_state.datos_paciente: st.session_state.datos_paciente['vital_signs'] = {}
                        st.session_state.datos_paciente['vital_signs']['fc'] = float(random.randint(60, 100))
                        st.session_state.datos_paciente['vital_signs']['spo2'] = float(random.randint(95, 99))
                    
                    if "Monitor Multiparamétrico" in devices or "Tensiómetro Digital" in devices:
                        if 'vital_signs' not in st.session_state.datos_paciente: st.session_state.datos_paciente['vital_signs'] = {}
                        st.session_state.datos_paciente['vital_signs']['pas'] = float(random.randint(110, 140))
                        st.session_state.datos_paciente['vital_signs']['pad'] = float(random.randint(70, 90))
                        
                    if "Monitor Multiparamétrico" in devices or "Termómetro Digital" in devices:
                        if 'vital_signs' not in st.session_state.datos_paciente: st.session_state.datos_paciente['vital_signs'] = {}
                        st.session_state.datos_paciente['vital_signs']['temp'] = round(random.uniform(36.0, 37.5), 1)
                        
                    st.success(f"Datos recibidos de: {', '.join(devices)}")
                    st.rerun()
    # ----------------------

    with st.container(border=True):
        st.markdown('<span class="vital-signs-grid" style="display:none"></span>', unsafe_allow_html=True)
        
        # Fila 1: Circulación (FC, PAS, PAD)
        c1, c2, c3 = st.columns(3)
        render_vital_sign_input(c1, "fc", "💓 Frecuencia Cardíaca", "lpm", 0.0, 300.0, 80.0, 1.0, "Latidos por minuto", configs.get("fc"))
        render_vital_sign_input(c2, "pas", "🩸 Presión Art. Sistólica", "mmHg", 0.0, 300.0, 120.0, 1.0, "Tensión Alta", configs.get("pas"))
        render_vital_sign_input(c3, "pad", "🩸 Presión Art. Diastólica", "mmHg", 0.0, 200.0, 80.0, 1.0, "Tensión Baja", configs.get("pad"))
        
        # Fila 2: Respiratorio y Temperatura (SpO2, FR, Temp)
        c4, c5, c6 = st.columns(3)
        render_vital_sign_input(c4, "spo2", "🫧 Saturación O2", "%", 0.0, 100.0, 98.0, 1.0, "Porcentaje de oxígeno", configs.get("spo2"))
        render_vital_sign_input(c5, "fr", "🫁 Frecuencia Respiratoria", "rpm", 0.0, 100.0, 16.0, 1.0, "Respiraciones por minuto", configs.get("fr"))
        render_vital_sign_input(c6, "temp", "🌡️ Temperatura", "°C", 20.0, 45.0, 36.5, 0.1, "Temperatura axilar/timpánica", configs.get("temp"))

        # Fila 3: Neurológico y Otros (GCS, Pupilas, Hidratación/O2)
        c7, c8, c9 = st.columns(3)
        
        # GCS
        render_vital_sign_input(c7, "gcs", "🧠 Escala Glasgow", "pts", 3.0, 15.0, 15.0, 1.0, "Nivel de conciencia (3-15)", configs.get("gcs"))

        # Pupilas
        with c8:
            pupilas_opts = ["Normal", "Lenta", "Fijas", "Anisocoria", "Puntiformes"]
            current_pupilas = st.session_state.datos_paciente.get('vital_signs', {}).get('pupilas', "Normal")
            pupilas = st.selectbox(
                "👁️ Reacción Pupilar", 
                pupilas_opts, 
                index=pupilas_opts.index(current_pupilas) if current_pupilas in pupilas_opts else 0, 
                key="vs_pupilas",
                help="Normal: Reactivas y simétricas"
            )
            if 'vital_signs' not in st.session_state.datos_paciente: st.session_state.datos_paciente['vital_signs'] = {}
            st.session_state.datos_paciente['vital_signs']['pupilas'] = pupilas
            
            p_map = {"Normal": "🟢", "Lenta": "🟡", "Fijas": "🟠", "Anisocoria": "🔴", "Puntiformes": "🔴"}
            st.caption(f"Gravedad: {p_map.get(pupilas, '⚪')}")

        # Hidratación y O2
        with c9:
             hyd_opts = ["Normal", "Deshidratación Leve", "Deshidratación Moderada", "Shock/Severa"]
             current_hyd = st.session_state.datos_paciente.get('vital_signs', {}).get('hidratacion', "Normal")
             hyd = st.selectbox(
                 "💧 Estado Hidratación",
                 hyd_opts,
                 index=hyd_opts.index(current_hyd) if current_hyd in hyd_opts else 0,
                 key="vs_hyd",
                 help="Evaluar mucosas, turgencia piel"
             )
             st.session_state.datos_paciente['vital_signs']['hidratacion'] = hyd
             
             o2 = st.checkbox(
                "😷 Oxígeno Suplementario", 
                value=st.session_state.datos_paciente.get('vital_signs', {}).get('oxigeno_suplementario', False), 
                key="vs_o2",
                help="Marcar si el paciente recibe oxígeno extra"
            )
             st.session_state.datos_paciente['vital_signs']['oxigeno_suplementario'] = o2

        # Fila 4: Dolor (EVA) - Integrado desde HDA/Entrevista
        st.divider()
        c_eva, _ = st.columns([1, 2])
        with c_eva:
            # Recuperar dolor de session_state (puede venir de 'dolor' o 'hda_intensidad')
            pain_level = st.session_state.datos_paciente.get('dolor', 0)
            if not pain_level:
                pain_level = st.session_state.datos_paciente.get('hda_intensidad', 0)
            
            # Asegurar que esté en vital_signs para el cálculo
            st.session_state.datos_paciente['vital_signs']['dolor'] = pain_level
            
            st.markdown(f"**⚡ Escala de Dolor (EVA):** {pain_level}/10")
            st.progress(int(pain_level) / 10)
            if int(pain_level) >= 7:
                st.error("Dolor Severo/Insoportable")
            elif int(pain_level) >= 4:
                st.warning("Dolor Moderado")
            else:
                st.success("Dolor Leve/Controlado")

    # --- RESULTADO EN TIEMPO REAL ---
    st.markdown("### 🚦 Indicadores de Triaje")
    
    # 1. Triaje Vital (Peor Caso)
    result = calculate_worst_case(st.session_state.datos_paciente.get('vital_signs', {}), configs)
    
    # 2. NEWS2
    news_result = calculate_news_score(st.session_state.datos_paciente.get('vital_signs', {}))
    
    # 3. PTR (Puntuación Total de Riesgo)
    ptr_result = calculate_ptr_score(
        st.session_state.datos_paciente.get('vital_signs', {}),
        st.session_state.datos_paciente # Pasamos todo el dict como contexto (tiene flags)
    )
    
    # Mapeo de colores CSS
    css_colors = {
        "green": "#28a745", "yellow": "#ffc107", "orange": "#fd7e14", "red": "#dc3545", "black": "#343a40", "gray": "#6c757d"
    }
    
    col_ind1, col_ind2, col_ind3 = st.columns(3)
    
    # Indicador 1: Triaje Vital
    with col_ind1:
        bg = css_colors.get(result["final_color"], "#6c757d")
        fg = "black" if result["final_color"] == "yellow" else "white"
        st.markdown(f"""
            <div style="background-color: {bg}; color: {fg}; padding: 15px; border-radius: 8px; text-align: center;">
                <h4 style="margin:0;">Triaje Vital</h4>
                <h2 style="margin:0;">{result['label']}</h2>
                <p style="margin:5px 0 0 0;">Espera: {result['wait_time']}</p>
            </div>
        """, unsafe_allow_html=True)

    # Indicador 2: NEWS2
    with col_ind2:
        bg = css_colors.get(news_result['color'], "#6c757d")
        fg = "black" if news_result['color'] == "yellow" else "white"
        st.markdown(f"""
            <div style="background-color: {bg}; color: {fg}; padding: 15px; border-radius: 8px; text-align: center;">
                <h4 style="margin:0;">NEWS2</h4>
                <h2 style="margin:0;">Score: {news_result['score']}</h2>
                <p style="margin:5px 0 0 0;">{news_result['risk']}</p>
            </div>
        """, unsafe_allow_html=True)

    # Indicador 3: PTR
    with col_ind3:
        bg = css_colors.get(ptr_result['color'], "#6c757d")
        fg = "black" if ptr_result['color'] == "yellow" else "white"
        st.markdown(f"""
            <div style="background-color: {bg}; color: {fg}; padding: 15px; border-radius: 8px; text-align: center;">
                <h4 style="margin:0;">PTR (Gemini)</h4>
                <h2 style="margin:0;">Puntos: {ptr_result['score']}</h2>
                <p style="margin:5px 0 0 0;">{ptr_result['level_text']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Detalles (Expandible)
    with st.expander("🔍 Ver desglose detallado de indicadores"):
        t1, t2, t3 = st.tabs(["Triaje Vital", "NEWS2", "PTR"])
        
        with t1:
            for det in result["details"]:
                metric = det.get('metric', '').upper()
                st.write(f"- **{metric}**: {det.get('value')} ({det.get('label')})")
        
        with t2:
            for det in news_result["details"]:
                st.write(f"- {det}")
            st.info(f"Acción sugerida: {news_result['action']}")
            
        with t3:
            for det in ptr_result["details"]:
                st.write(f"- {det}")
            st.caption("Puntuación Total de Riesgo basada en multiplicadores y contexto.")

    st.markdown('<div class="debug-footer">src/components/triage/vital_signs/form.py</div>', unsafe_allow_html=True)
