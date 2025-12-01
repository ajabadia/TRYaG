# path: src/components/triage/vital_signs/input.py
import streamlit as st
from typing import Optional, Any
from components.triage.triage_logic import evaluate_vital_sign

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
        
        # Lógica de Tooltip y Default desde Config
        final_help = help_text
        input_default = default # Fallback
        
        if config:
            # Helper para acceso seguro (obj o dict)
            def get_val(obj, key, default=None):
                if isinstance(obj, dict): return obj.get(key, default)
                return getattr(obj, key, default)

            c_min = get_val(config, 'val_min')
            c_max = get_val(config, 'val_max')
            n_min = get_val(config, 'normal_min')
            n_max = get_val(config, 'normal_max')
            c_def = get_val(config, 'default_value')
            
            if c_def is not None:
                input_default = float(c_def)
                
            info_str = f"\n\n📊 Rangos para edad:\n- Normal: {n_min} - {n_max}\n- Mín/Máx: {c_min} - {c_max}\n- Defecto: {c_def}"
            final_help += info_str

        # Si no hay valor actual, usar el default de la config (o el fallback)
        val_to_show = float(current_val) if current_val is not None else input_default

        val = st.number_input(
            f"{label} ({unit})", 
            min_value=min_val, 
            max_value=max_val, 
            value=val_to_show,
            step=step,
            key=f"vs_{metric_key}",
            help=final_help,
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
