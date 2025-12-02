import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# from sklearn.metrics import confusion_matrix, accuracy_score # Removed to avoid dependency

def render_concordance_analysis(df_audit, key_prefix="concordance"):
    """
    Renderiza el análisis de concordancia entre la IA y el triaje humano.
    Calcula métricas de precisión, sobre-triaje y sub-triaje.
    """
    st.markdown("### ⚖️ Auditoría de Concordancia (Validación Científica)")
    
    if df_audit.empty:
        st.info("No hay datos disponibles para el análisis.")
        return

    # Filtrar solo registros con decisión humana y sugerencia IA válidas
    # Asumimos que 'nivel_corregido' es la verdad terreno (Human) y 'sugerencia_ia' es la predicción
    # Asegurarnos de tener columnas numéricas
    
    # Pre-procesamiento
    valid_data = df_audit.dropna(subset=['nivel_corregido', 'sugerencia_ia']).copy()
    
    # Convertir a enteros si es posible
    try:
        valid_data['human_level'] = pd.to_numeric(valid_data['nivel_corregido'], errors='coerce')
        valid_data['ai_level'] = pd.to_numeric(valid_data['sugerencia_ia'], errors='coerce')
        valid_data = valid_data.dropna(subset=['human_level', 'ai_level'])
        valid_data['human_level'] = valid_data['human_level'].astype(int)
        valid_data['ai_level'] = valid_data['ai_level'].astype(int)
    except Exception as e:
        st.error(f"Error procesando datos numéricos: {e}")
        return

    if valid_data.empty:
        st.warning("No hay suficientes datos validados (con nivel IA y Humano) para el análisis.")
        return

    # --- MÉTRICAS CLAVE ---
    y_true = valid_data['human_level']
    y_pred = valid_data['ai_level']
    
    # accuracy = accuracy_score(y_true, y_pred)
    accuracy = (y_true == y_pred).mean()
    
    # Sobre-triaje: IA dice más grave (menor número) que Humano
    # Ej: IA=2 (Naranja), Humano=4 (Verde) -> IA < Humano
    over_triage = len(valid_data[valid_data['ai_level'] < valid_data['human_level']]) / len(valid_data)
    
    # Sub-triaje: IA dice menos grave (mayor número) que Humano
    # Ej: IA=4 (Verde), Humano=2 (Naranja) -> IA > Humano
    under_triage = len(valid_data[valid_data['ai_level'] > valid_data['human_level']]) / len(valid_data)

    col1, col2, col3 = st.columns(3)
    col1.metric("Precisión Global (Accuracy)", f"{accuracy:.1%}", help="Porcentaje de casos donde IA y Humano coinciden exactamente.")
    col2.metric("Sobre-triaje (Falsos Positivos)", f"{over_triage:.1%}", help="IA asignó mayor gravedad que el humano (Seguro pero consume recursos).")
    col3.metric("Sub-triaje (Falsos Negativos)", f"{under_triage:.1%}", help="IA asignó menor gravedad que el humano (Riesgo clínico).", delta_color="inverse")

    st.divider()

    # --- VISUALIZACIONES ---
    tab_matrix, tab_scatter, tab_dist = st.tabs(["Matriz de Confusión", "Dispersión", "Distribución de Errores"])

    with tab_matrix:
        st.markdown("#### Matriz de Confusión")
        st.caption("Eje X: Nivel IA (Predicción) | Eje Y: Nivel Humano (Real)")
        
        labels = sorted(list(set(y_true.unique()) | set(y_pred.unique())))
        
        # cm = confusion_matrix(y_true, y_pred, labels=labels)
        # Implementación con Pandas
        cm_df = pd.crosstab(y_true, y_pred, rownames=['Real'], colnames=['Predicción'])
        cm_df = cm_df.reindex(index=labels, columns=labels, fill_value=0)
        cm = cm_df.values
        
        fig_cm = px.imshow(cm,
                           labels=dict(x="Nivel IA", y="Nivel Humano", color="Cantidad"),
                           x=labels,
                           y=labels,
                           text_auto=True,
                           color_continuous_scale="Blues")
        fig_cm.update_layout(xaxis_title="Nivel Sugerido por IA", yaxis_title="Nivel Real (Humano)")
        st.plotly_chart(fig_cm, use_container_width=True)

    with tab_scatter:
        st.markdown("#### Correlación Visual")
        # Jitter para ver mejor los puntos superpuestos
        valid_data['jitter_ai'] = valid_data['ai_level'] + (pd.Series([0.1]*len(valid_data)).sample(len(valid_data), replace=True).values * (pd.Series([-1, 1]).sample(len(valid_data), replace=True).values))
        valid_data['jitter_human'] = valid_data['human_level'] + (pd.Series([0.1]*len(valid_data)).sample(len(valid_data), replace=True).values * (pd.Series([-1, 1]).sample(len(valid_data), replace=True).values))
        
        fig_sc = px.scatter(valid_data, x="ai_level", y="human_level", color="human_level",
                            title="Nivel IA vs Nivel Humano (con Jitter)",
                            labels={"ai_level": "Nivel IA", "human_level": "Nivel Humano"},
                            trendline="ols")
        # Línea de identidad perfecta
        fig_sc.add_shape(type="line", x0=1, y0=1, x1=5, y1=5, line=dict(color="Red", width=2, dash="dash"))
        st.plotly_chart(fig_sc, use_container_width=True)

    with tab_dist:
        st.markdown("#### Análisis de Desviación")
        # Calcular diferencia: Humano - IA
        # 0 = Perfecto
        # Positivo (ej: 4 - 2 = +2) -> IA dijo 2 (Grave), Humano 4 (Leve) -> Sobre-triaje (IA exageró)
        # Negativo (ej: 2 - 4 = -2) -> IA dijo 4 (Leve), Humano 2 (Grave) -> Sub-triaje (IA subestimó)
        
        valid_data['diff'] = valid_data['human_level'] - valid_data['ai_level']
        
        diff_counts = valid_data['diff'].value_counts().sort_index()
        
        fig_bar = px.bar(x=diff_counts.index, y=diff_counts.values,
                         labels={'x': 'Diferencia (Nivel Humano - Nivel IA)', 'y': 'Cantidad de Casos'},
                         title="Distribución de Errores (0 = Acierto)",
                         color=diff_counts.index,
                         color_continuous_scale="RdBu")
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.info("""
        **Interpretación de la Diferencia:**
        * **0**: Concordancia Perfecta.
        * **Positivo (+)**: La IA asignó un nivel más bajo (más grave) que el humano. (Sobre-triaje).
        * **Negativo (-)**: La IA asignó un nivel más alto (menos grave) que el humano. (Sub-triaje).
        """)

    st.markdown('<div class="debug-footer">src/components/analytics/concordance_analysis.py</div>', unsafe_allow_html=True)
