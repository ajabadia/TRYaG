import streamlit as st
from typing import Dict, Any, Optional, List
from src.db.repositories.vital_signs_repo import VitalSignsRepository
from src.components.triage.triage_logic import calculate_worst_case, evaluate_vital_sign, calculate_news_score

def get_all_configs(age: int) -> Dict[str, Any]:
    """Carga todas las configuraciones de signos vitales para la edad dada."""
    repo = VitalSignsRepository()
    configs = {}
    for metric in ["fc", "spo2", "temp", "pas", "pad", "fr", "gcs"]:
        configs[metric] = repo.get_config(metric, age)
    return configs

def render_vital_sign_input(
    col, 
    metric_key: str, 
    label: str, 
    unit: str, 
    min_val: float, 
    max_val: float, 
    default: float, 
    step: float, 
    help_text: str,
    config: Optional[Any] = None
):
    """Helper para renderizar un input de signo vital con feedback visual inmediato."""
    with col:
        current_val = st.session_state.datos_paciente.get('vital_signs', {}).get(metric_key)
        
        # Si no hay valor actual, usar None para permitir placeholder o vacío si se desea, 
        # pero number_input requiere un valor numérico por defecto.
        # Usamos el default si no existe.
        val = st.number_input(
            f"{label} ({unit})", 
            min_value=min_val, 
            max_value=max_val, 
            value=float(current_val) if current_val is not None else None,
            step=step,
            key=f"vs_{metric_key}",
            help=help_text,
            placeholder="-"
        )
        
        # Guardar en estado
        if 'vital_signs' not in st.session_state.datos_paciente:
            st.session_state.datos_paciente['vital_signs'] = {}
            
        st.session_state.datos_paciente['vital_signs'][metric_key] = val
        
        # Feedback visual inmediato (simulado o calculado)
        if val is not None and config:
            # Evaluar
            prio, color, _ = evaluate_vital_sign(val, config)
            # Mostrar indicador
            color_map = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴", "gray": "⚪"}
            st.caption(f"Nivel: {color_map.get(color, '⚪')}")

def render_vital_signs_form(age: int = 40):
    """Renderiza el formulario completo de signos vitales."""
    st.subheader("2. Signos Vitales")
    
    if age is None: age = 40
    
    # Cargar configuraciones una sola vez
    configs = get_all_configs(age)
    
    # CSS para Grid Responsivo
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.vital-signs-grid) [data-testid="stHorizontalBlock"],
        div[data-testid="stVerticalBlock"]:has(.vital-signs-grid) [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            flex-direction: row !important;
            gap: 15px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.vital-signs-grid) [data-testid="column"],
        div[data-testid="stVerticalBlock"]:has(.vital-signs-grid) [data-testid="column"] {
            flex: 1 1 200px !important; /* Un poco más ancho para sliders */
            min-width: 200px !important;
            max-width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<span class="vital-signs-grid" style="display:none"></span>', unsafe_allow_html=True)
        
        # Fila 1: FC, SpO2, Temp
        c1, c2, c3 = st.columns(3)
        render_vital_sign_input(c1, "fc", "Frecuencia Cardíaca", "lpm", 0.0, 300.0, 80.0, 1.0, "Latidos por minuto", configs.get("fc"))
        render_vital_sign_input(c2, "spo2", "Saturación O2", "%", 0.0, 100.0, 98.0, 1.0, "Porcentaje de oxígeno", configs.get("spo2"))
        render_vital_sign_input(c3, "temp", "Temperatura", "°C", 20.0, 45.0, 36.5, 0.1, "Temperatura axilar/timpánica", configs.get("temp"))
        
        # Fila 2: TA (PAS/PAD), FR, GCS
        c4, c5, c6 = st.columns(3)
        # PAS
        render_vital_sign_input(c4, "pas", "Presión Art. Sistólica", "mmHg", 0.0, 300.0, 120.0, 1.0, "Tensión Alta", configs.get("pas"))
        # FR
        render_vital_sign_input(c5, "fr", "Frecuencia Respiratoria", "rpm", 0.0, 100.0, 16.0, 1.0, "Respiraciones por minuto", configs.get("fr"))
        # GCS (Glasgow)
        render_vital_sign_input(c6, "gcs", "Escala Glasgow", "pts", 3.0, 15.0, 15.0, 1.0, "Nivel de conciencia (3-15)", configs.get("gcs"))

        # Fila 3: Pupilas y O2 y Hidratación
        c_pup, c_o2, c_hyd = st.columns([2, 1, 2])
        with c_pup:
            pupilas_opts = ["Normal", "Lenta", "Fijas", "Anisocoria", "Puntiformes"]
            current_pupilas = st.session_state.datos_paciente.get('vital_signs', {}).get('pupilas', "Normal")
            pupilas = st.selectbox(
                "Reacción Pupilar", 
                pupilas_opts, 
                index=pupilas_opts.index(current_pupilas) if current_pupilas in pupilas_opts else 0, 
                key="vs_pupilas",
                help="Normal: Reactivas y simétricas"
            )
            
            if 'vital_signs' not in st.session_state.datos_paciente: st.session_state.datos_paciente['vital_signs'] = {}
            st.session_state.datos_paciente['vital_signs']['pupilas'] = pupilas
            
            # Feedback Pupilas (Hardcoded visual)
            p_map = {"Normal": "🟢", "Lenta": "🟡", "Fijas": "🟠", "Anisocoria": "🔴", "Puntiformes": "🔴"}
            st.caption(f"Gravedad: {p_map.get(pupilas, '⚪')}")

        with c_o2:
            o2 = st.checkbox(
                "Oxígeno Suplementario", 
                value=st.session_state.datos_paciente.get('vital_signs', {}).get('oxigeno_suplementario', False), 
                key="vs_o2",
                help="Marcar si el paciente recibe oxígeno extra"
            )
            st.session_state.datos_paciente['vital_signs']['oxigeno_suplementario'] = o2

        with c_hyd:
             hyd_opts = ["Normal", "Deshidratación Leve", "Deshidratación Moderada", "Shock/Severa"]
             current_hyd = st.session_state.datos_paciente.get('vital_signs', {}).get('hidratacion', "Normal")
             hyd = st.selectbox(
                 "Estado Hidratación",
                 hyd_opts,
                 index=hyd_opts.index(current_hyd) if current_hyd in hyd_opts else 0,
                 key="vs_hyd",
                 help="Evaluar mucosas, turgencia piel"
             )
             st.session_state.datos_paciente['vital_signs']['hidratacion'] = hyd

    # --- RESULTADO EN TIEMPO REAL ---
    st.markdown("### 🚦 Resultado de Triaje (Signos Vitales)")
    
    # Calcular resultado Triaje
    result = calculate_worst_case(st.session_state.datos_paciente.get('vital_signs', {}), configs)
    
    # Calcular NEWS
    news_result = calculate_news_score(st.session_state.datos_paciente.get('vital_signs', {}))
    
    final_color = result["final_color"]
    final_label = result["label"]
    wait_time = result["wait_time"]
    
    # Mapeo de colores CSS
    css_colors = {
        "green": "#28a745", "yellow": "#ffc107", "orange": "#fd7e14", "red": "#dc3545", "black": "#343a40", "gray": "#6c757d"
    }
    bg_color = css_colors.get(final_color, "#6c757d")
    text_color = "black" if final_color == "yellow" else "white"
    
    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.markdown(f"""
            <div style="background-color: {bg_color}; color: {text_color}; padding: 20px; border-radius: 10px; text-align: center; margin-top: 10px;">
                <h3 style="margin:0;">Triaje: {final_label}</h3>
                <p style="margin:5px 0 0 0; font-size: 1em;">Espera Máx: <strong>{wait_time}</strong></p>
            </div>
        """, unsafe_allow_html=True)
        
    with c_res2:
        n_color = news_result['color']
        n_score = news_result['score']
        n_risk = news_result['risk']
        bg_color_n = css_colors.get(n_color, "#6c757d")
        text_color_n = "black" if n_color == "yellow" else "white"
        
        st.markdown(f"""
            <div style="background-color: {bg_color_n}; color: {text_color_n}; padding: 20px; border-radius: 10px; text-align: center; margin-top: 10px;">
                <h3 style="margin:0;">NEWS2: {n_score}</h3>
                <p style="margin:5px 0 0 0; font-size: 1em;">Riesgo: <strong>{n_risk}</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    # Detalles (Expandible)
    with st.expander("Ver detalles de clasificación y NEWS"):
        c_det1, c_det2 = st.columns(2)
        with c_det1:
            st.markdown("##### Triaje")
            for det in result["details"]:
                st.write(f"- {det}")
        with c_det2:
            st.markdown("##### NEWS2")
            for det in news_result["details"]:
                st.write(f"- {det}")
            st.caption(f"Acción: {news_result['action']}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/vital_signs_form.py</div>', unsafe_allow_html=True)
