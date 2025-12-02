"""
Panel de configuración para la Puntuación Total de Riesgo (PTR).
Permite editar multiplicadores y reglas de cálculo.
"""
import streamlit as st
import pandas as pd
from db.repositories.ptr_config import get_ptr_config_repository, PTRConfig, PTRRule

def render_ptr_config_panel():
    st.header("⚙️ Configuración PTR (Puntuación Total de Riesgo)")
    st.info("Ajuste los multiplicadores y reglas para el cálculo automático del nivel de riesgo.")

    repo = get_ptr_config_repository()
    configs = repo.get_all_configs()
    
    if not configs:
        st.warning("No hay configuraciones disponibles. Inicializando valores por defecto...")
        repo.initialize_defaults()
        st.rerun()
        return

    # Selector de métrica
    metric_options = {c.metric_key: c.name for c in configs}
    selected_key = st.selectbox(
        "Seleccione la métrica a configurar:",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )

    if not selected_key:
        return

    # Obtener config seleccionada
    config = next((c for c in configs if c.metric_key == selected_key), None)
    if not config:
        st.error("Error al cargar la configuración.")
        return

    st.divider()
    
    with st.form(key=f"form_ptr_{selected_key}"):
        st.subheader(f"Configuración: {config.name}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            base_mult = st.number_input(
                "Multiplicador Base",
                min_value=0.0,
                value=float(config.base_multiplier),
                step=0.5,
                help="Factor por el que se multiplican los puntos de las reglas."
            )
            
        with col2:
            geriatric_mult = st.number_input(
                "Mult. Geriátrico",
                min_value=0.0,
                value=float(config.geriatric_multiplier) if config.geriatric_multiplier else 0.0,
                step=0.5,
                help="Factor alternativo si el paciente es geriátrico (0 = No aplica)."
            )
            
        with col3:
            immuno_mult = st.number_input(
                "Mult. Inmunodeprimido",
                min_value=0.0,
                value=float(config.immuno_multiplier) if config.immuno_multiplier else 0.0,
                step=0.5,
                help="Factor alternativo si el paciente es inmunodeprimido (0 = No aplica)."
            )

        st.markdown("#### Reglas de Puntuación")
        st.caption("Defina los umbrales y los puntos base que se asignan antes de aplicar el multiplicador.")

        # Preparar datos para editor
        rules_data = []
        for r in config.rules:
            rules_data.append({
                "operator": r.operator,
                "value": r.value,
                "value_max": r.value_max,
                "points": r.points,
                "description": r.description
            })
        
        df_rules = pd.DataFrame(rules_data)
        
        column_config = {
            "operator": st.column_config.SelectboxColumn(
                "Operador",
                options=["<", "<=", ">", ">=", "==", "between"],
                required=True,
                width="small"
            ),
            "value": st.column_config.NumberColumn(
                "Valor Ref.",
                required=True,
                step=0.1,
                format="%.1f"
            ),
            "value_max": st.column_config.NumberColumn(
                "Valor Max (Between)",
                help="Solo para operador 'between'",
                step=0.1,
                format="%.1f"
            ),
            "points": st.column_config.NumberColumn(
                "Puntos Base",
                required=True,
                min_value=0,
                step=1
            ),
            "description": st.column_config.TextColumn(
                "Descripción",
                width="medium"
            )
        }

        edited_df = st.data_editor(
            df_rules,
            column_config=column_config,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_ptr_{selected_key}"
        )

        submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
        
        if submitted:
            # Reconstruir objeto config
            new_rules = []
            for _, row in edited_df.iterrows():
                # Validar datos básicos
                if pd.isna(row["value"]) or pd.isna(row["points"]):
                    continue
                    
                new_rules.append(PTRRule(
                    operator=row["operator"],
                    value=float(row["value"]),
                    value_max=float(row["value_max"]) if not pd.isna(row["value_max"]) else None,
                    points=float(row["points"]),
                    description=str(row["description"]) if not pd.isna(row["description"]) else None
                ))
            
            # Actualizar config
            config.base_multiplier = base_mult
            config.geriatric_multiplier = geriatric_mult if geriatric_mult > 0 else None
            config.immuno_multiplier = immuno_mult if immuno_mult > 0 else None
            config.rules = new_rules
            
            if repo.save_config(config):
                st.success("Configuración guardada correctamente.")
                st.rerun()
            else:
                st.error("Error al guardar la configuración.")

    st.markdown('<div class="debug-footer">src/ui/config/ptr_config_panel.py</div>', unsafe_allow_html=True)
