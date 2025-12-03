# path: src/ui/config_panel/vital_signs_config.py
import streamlit as st
import pandas as pd
from db.repositories.vital_signs_repo import VitalSignsRepository
from db.models import VitalSignReference, VitalSignAgeConfig

def render_vital_signs_config():
    """Renderiza el panel de configuración de signos vitales."""
    st.subheader("📊 Configuración de Signos Vitales")
    st.info("Defina los rangos normales y límites de validación para cada signo vital según la edad.")
    
    repo = VitalSignsRepository()
    references = repo.get_all_references()
    
    if not references:
        st.warning("No hay configuraciones de signos vitales. Ejecute el script de inicialización.")
        return

    # Selector de Signo Vital
    signo_names = [ref.name for ref in references]
    selected_name = st.selectbox("Seleccione Signo Vital", signo_names)
    
    selected_ref = next((r for r in references if r.name == selected_name), None)
    
    if selected_ref:
        st.markdown(f"### {selected_ref.name} ({selected_ref.unit})")
        
        # Mostrar tabla de configuraciones actuales
        data = []
        for cfg in selected_ref.configs:
            data.append({
                "Edad Min": cfg.min_age,
                "Edad Max": cfg.max_age,
                "Límite Min (Error)": cfg.val_min,
                "Normal Min": cfg.normal_min,
                "Valor Medio": cfg.default_value,
                "Normal Max": cfg.normal_max,
                "Límite Max (Error)": cfg.val_max
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        st.divider()
        st.markdown("#### ✏️ Editar Rangos")
        
        # Editor simple: Seleccionar rango a editar
        rango_opts = [f"{cfg.min_age} - {cfg.max_age} años" for cfg in selected_ref.configs]
        selected_rango_str = st.selectbox("Seleccione rango de edad a editar", rango_opts)
        
        if selected_rango_str:
            idx = rango_opts.index(selected_rango_str)
            cfg = selected_ref.configs[idx]
            
            with st.form(key=f"edit_vs_{selected_ref.key}_{idx}"):
                c1, c2 = st.columns(2)
                with c1:
                    new_min_age = st.number_input("Edad Mínima", 0, 120, cfg.min_age)
                    new_val_min = st.number_input("Límite Absoluto Mínimo (Error)", 0.0, 1000.0, float(cfg.val_min))
                    new_normal_min = st.number_input("Mínimo Normal (Verde)", 0.0, 1000.0, float(cfg.normal_min))
                    new_default = st.number_input("Valor por Defecto (Media)", 0.0, 1000.0, float(cfg.default_value))
                with c2:
                    new_max_age = st.number_input("Edad Máxima", 0, 120, cfg.max_age)
                    new_val_max = st.number_input("Límite Absoluto Máximo (Error)", 0.0, 1000.0, float(cfg.val_max))
                    new_normal_max = st.number_input("Máximo Normal (Verde)", 0.0, 1000.0, float(cfg.normal_max))
                
                if st.form_submit_button("Guardar Cambios"):
                    # Actualizar objeto
                    cfg.min_age = new_min_age
                    cfg.max_age = new_max_age
                    cfg.val_min = new_val_min
                    cfg.val_max = new_val_max
                    cfg.normal_min = new_normal_min
                    cfg.normal_max = new_normal_max
                    cfg.default_value = new_default
                    
                    # Guardar en BD
                    # Convertir a dict para update
                    repo.update(selected_ref.id, selected_ref.model_dump(by_alias=True, exclude_none=True))
                    st.success("Configuración actualizada correctamente.")
                    st.rerun()

                    st.markdown('<div class="debug-footer">src/ui/config/vital_signs_config.py</div>', unsafe_allow_html=True)
