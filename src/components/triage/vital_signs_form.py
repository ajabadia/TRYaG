# path: src/components/triage/vital_signs_form.py
import streamlit as st
from typing import Dict, Any, Optional, List
from src.db.repositories.vital_signs_repo import VitalSignsRepository
from src.components.triage.triage_logic import calculate_worst_case, evaluate_vital_sign

def get_all_configs(age: int) -> Dict[str, Any]:
    """Obtiene todas las configuraciones para la edad dada."""
    repo = VitalSignsRepository()
    refs = repo.get_all_references()
    configs = {}
    for ref in refs:
        for cfg in ref.configs:
            if cfg.min_age <= age <= cfg.max_age:
                configs[ref.key] = cfg
                break
    return configs

def render_vital_sign_input(
    label: str, 
    key: str, 
    metric: str, 
    config: Any,
    widget_type: str = "number",
    step: float = 1.0, 
    help_text: str = None
):
    """Renderiza un input (slider o number) con feedback visual."""
    
    # Configuración por defecto si falla carga
    min_val = 0.0
    max_val = 1000.0
    default_val = None
    
    if config:
        min_val = float(config.val_min)
        max_val = float(config.val_max)
        default_val = float(config.default_value)
    
    # Obtener valor actual
    current_val = st.session_state.datos_paciente.get('vital_signs', {}).get(metric)
    
    # Inicializar con default si es None
    if current_val is None and default_val is not None:
        current_val = default_val

    # Renderizar Widget
    val = None
    if widget_type == "slider":
        # Asegurar rango válido para slider
        s_min = max(min_val, 0.0) # Evitar negativos raros si no aplica
        s_max = min(max_val, 300.0) # Cap visual razonable
        
        # Ajustes específicos por métrica para UX (Rangos visuales útiles, no absolutos de error)
        if metric == "fc": s_min, s_max = 30.0, 200.0
        if metric == "spo2": s_min, s_max = 70.0, 100.0
        if metric == "eva": s_min, s_max = 0.0, 10.0
        
        val = st.slider(
            label, 
            min_value=float(s_min), 
            max_value=float(s_max), 
            value=float(current_val) if current_val is not None else float(s_min),
            step=step,
            key=key,
            help=help_text
        )
    else:
        val = st.number_input(
            label, 
            min_value=min_val, 
            max_value=max_val, 
            value=float(current_val) if current_val is not None else None, 
            step=step,
            key=key,
            help=help_text
        )
    
    # Guardar y Evaluar
    if 'vital_signs' not in st.session_state.datos_paciente:
        st.session_state.datos_paciente['vital_signs'] = {}
    
    if val is not None:
        st.session_state.datos_paciente['vital_signs'][metric] = val
        
        # Feedback Visual Inmediato
        if config:
            color, _, label_txt = evaluate_vital_sign(val, config)
            
            color_map = {
                "red": "🔴", "orange": "🟠", "yellow": "🟡", "green": "🟢", "gray": "⚪", "black": "⚫"
            }
            st.caption(f"{color_map.get(color, '⚪')} {label_txt}")

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
        
        # Helper para generar help text
        def get_help(cfg):
            if not cfg: return None
            return f"Normal: {cfg.normal_min} - {cfg.normal_max}"

        # Fila 1: Sliders Principales (FC, SpO2, EVA)
        c1, c2, c3 = st.columns(3)
        with c1:
            cfg = configs.get("fc")
            render_vital_sign_input("Frecuencia Cardíaca (ppm)", "vs_fc", "fc", cfg, widget_type="slider", step=1.0, help_text=get_help(cfg))
        with c2:
            cfg = configs.get("spo2")
            render_vital_sign_input("Saturación O2 (%)", "vs_spo2", "spo2", cfg, widget_type="slider", step=1.0, help_text=get_help(cfg))
        with c3:
            cfg = configs.get("eva")
            render_vital_sign_input("Escala Dolor (EVA)", "vs_eva", "eva", cfg, widget_type="slider", step=1.0, help_text=get_help(cfg))
            
        st.divider()
        
        # Fila 2: Inputs Numéricos (Temp, PAS, PAD, FR, GCS)
        cols = st.columns(5)
        with cols[0]:
            cfg = configs.get("temp")
            render_vital_sign_input("Temp (°C)", "vs_temp", "temp", cfg, step=0.1, help_text=get_help(cfg))
        with cols[1]:
            cfg = configs.get("pas")
            render_vital_sign_input("PAS (mmHg)", "vs_pas", "pas", cfg, step=1.0, help_text=get_help(cfg))
        with cols[2]:
            cfg = configs.get("pad")
            render_vital_sign_input("PAD (mmHg)", "vs_pad", "pad", cfg, step=1.0, help_text=get_help(cfg))
        with cols[3]:
            cfg = configs.get("fr")
            render_vital_sign_input("FR (rpm)", "vs_fr", "fr", cfg, step=1.0, help_text=get_help(cfg))
        with cols[4]:
            cfg = configs.get("gcs")
            render_vital_sign_input("Glasgow", "vs_gcs", "gcs", cfg, step=1.0, help_text=get_help(cfg))
            
        st.divider()
        
        # Fila 3: Pupilas y O2
        c_pup, c_o2 = st.columns([2, 1])
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

    # --- RESULTADO EN TIEMPO REAL ---
    st.markdown("### 🚦 Resultado de Triaje (Signos Vitales)")
    
    # Calcular resultado
    result = calculate_worst_case(st.session_state.datos_paciente.get('vital_signs', {}), configs)
    
    final_color = result["final_color"]
    final_label = result["label"]
    wait_time = result["wait_time"]
    
    # Mapeo de colores CSS
    css_colors = {
        "green": "#28a745", "yellow": "#ffc107", "orange": "#fd7e14", "red": "#dc3545", "black": "#343a40", "gray": "#6c757d"
    }
    bg_color = css_colors.get(final_color, "#6c757d")
    text_color = "black" if final_color == "yellow" else "white"
    
    st.markdown(f"""
        <div style="background-color: {bg_color}; color: {text_color}; padding: 20px; border-radius: 10px; text-align: center; margin-top: 10px;">
            <h2 style="margin:0;">{final_label}</h2>
            <p style="margin:5px 0 0 0; font-size: 1.2em;">Tiempo Máximo de Atención: <strong>{wait_time}</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Detalles (Expandible)
    with st.expander("Ver detalles de clasificación"):
        for det in result["details"]:
            icon = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴", "black": "⚫", "gray": "⚪"}.get(det['color'], '⚪')
            st.markdown(f"**{det['metric'].upper()}**: {det['value']} -> {icon} {det['label']}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/vital_signs_form.py</div>', unsafe_allow_html=True)
