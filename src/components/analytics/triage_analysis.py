# path: src/components/analytics/triage_analysis.py
"""
Componente de análisis de triaje con 5 subpestañas.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.icon_utils import get_icon_html

def render_triage_analysis(df_audit, key_prefix="triage"):
    """
    Renderiza análisis completo de triaje en subpestañas.
    """
    st.markdown(f"### {get_icon_html('medical', 24)}Análisis de Triaje", unsafe_allow_html=True)
    
    if df_audit.empty:
        st.info("No hay datos de triaje disponibles.")
        return

    # --- Filtros Locales ---
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        niveles_disponibles = df_audit['nivel_corregido'].unique().tolist()
        selected_niveles = st.multiselect(
            "Filtrar por Nivel de Triaje",
            options=niveles_disponibles,
            default=niveles_disponibles,
            key=f"{key_prefix}_filter_nivel"
        )
        
    with col_f2:
        if 'decision_humana' in df_audit.columns:
            decisiones_disponibles = df_audit['decision_humana'].dropna().unique().tolist()
            selected_decisiones = st.multiselect(
                "Filtrar por Decisión Humana",
                options=decisiones_disponibles,
                default=decisiones_disponibles,
                key=f"{key_prefix}_filter_decision"
            )
        else:
            selected_decisiones = []

    if selected_niveles:
        df_audit = df_audit[df_audit['nivel_corregido'].isin(selected_niveles)]
        
    if 'decision_humana' in df_audit.columns and selected_decisiones:
        df_audit = df_audit[df_audit['decision_humana'].isin(selected_decisiones)]
    
    if df_audit.empty:
        st.warning("No hay datos para los niveles seleccionados.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        ":material/bar_chart: Distribución de Niveles", 
        ":material/compare_arrows: Comparativa IA vs Humano", 
        ":material/healing: Dolor por Nivel", 
        ":material/star_rate: Calidad de Sugerencias", 
        ":material/warning: Análisis de Discrepancias"
    ])
    
    # Tab 1: Distribución de Niveles
    with tab1:
        st.markdown("#### Distribución de Niveles de Triaje")
        chart_type = st.radio("Tipo de Gráfico", ["Barras", "Donut"], key=f"{key_prefix}_chart_niveles", horizontal=True)
        
        nivel_counts = df_audit['nivel_corregido'].value_counts()
        
        if chart_type == "Barras":
            st.bar_chart(nivel_counts, use_container_width=True, color="#28a745")
        else:  # Donut
            fig, ax = plt.subplots()
            ax.pie(nivel_counts, labels=nivel_counts.index, autopct='%1.1f%%', 
                  startangle=90, wedgeprops=dict(width=0.3))
            ax.axis('equal')
            st.pyplot(fig)
            plt.close(fig)
    
    # Tab 2: Comparativa IA vs Humano
    with tab2:
        st.markdown("#### Comparativa: Sugerencia IA vs. Decisión Humana")
        chart_type_comp = st.radio("Tipo de Gráfico", ["Barras Agrupadas", "Barras Apiladas", "Área"], 
                                   key=f"{key_prefix}_chart_comparativa", horizontal=True)
        
        ia_counts = df_audit['sugerencia_ia'].value_counts().rename('Sugerencia IA')
        humano_counts = df_audit['nivel_corregido'].value_counts().rename('Decisión Humana')
        comparison_df = pd.concat([ia_counts, humano_counts], axis=1).fillna(0).astype(int)
        
        if chart_type_comp == "Barras Agrupadas":
            st.bar_chart(comparison_df, use_container_width=True)
        elif chart_type_comp == "Barras Apiladas":
            st.bar_chart(comparison_df, use_container_width=True, stack=True)
        else:  # Área
            st.area_chart(comparison_df, use_container_width=True)
    
    # Tab 3: Dolor por Nivel
    with tab3:
        st.markdown("#### Relación Dolor - Nivel de Triaje")
        chart_type_dolor = st.radio("Tipo de Gráfico", ["Barras (Promedio)", "Scatter (Dispersión)"], 
                                    key=f"{key_prefix}_chart_dolor", horizontal=True)
        
        if chart_type_dolor == "Barras (Promedio)":
            dolor_por_nivel = df_audit.groupby('nivel_corregido')['dolor'].mean().sort_values(ascending=False)
            st.bar_chart(dolor_por_nivel, use_container_width=True)
        else:  # Scatter
            st.scatter_chart(df_audit, x='nivel_corregido', y='dolor', color='nivel_corregido', 
                           use_container_width=True)
        
        st.divider()
        st.markdown("##### Distribuciones Complementarias")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Distribución de Edad**")
            st.bar_chart(df_audit['edad'].value_counts().sort_index(), use_container_width=True)
        with c2:
            st.markdown("**Distribución de Dolor (EVA)**")
            st.bar_chart(df_audit['dolor'].value_counts().sort_index(), use_container_width=True)
    
    # Tab 4: Calidad de Sugerencias
    with tab4:
        st.markdown("#### Calidad de la Sugerencia vs. Decisión Final")
        chart_type_cal = st.radio("Tipo de Gráfico", ["Barras Apiladas", "Barras Agrupadas"], 
                                  key=f"{key_prefix}_chart_calidad", horizontal=True)
        
        calidad_vs_decision_df = pd.crosstab(df_audit['decision_humana'], df_audit['calificacion_humana'])
        
        if chart_type_cal == "Barras Apiladas":
            st.bar_chart(calidad_vs_decision_df, use_container_width=True, stack=True)
        else:
            st.bar_chart(calidad_vs_decision_df, use_container_width=True, stack=False)
    
    # Tab 5: Análisis de Discrepancias
    with tab5:
        st.markdown("#### Análisis de Discrepancias")
        discrepancias_df = df_audit[df_audit['sugerencia_ia'] != df_audit['nivel_corregido']]
        
        if not discrepancias_df.empty:
            st.warning(f"Se han encontrado {len(discrepancias_df)} casos con discrepancia entre la IA y la decisión humana.")
            
            col_chart, col_table = st.columns([1, 1])
            with col_chart:
                st.markdown("##### Frecuencia de Discrepancias por Nivel")
                chart_type_disc = st.radio("Tipo de Gráfico", ["Barras Agrupadas", "Barras Apiladas", "Área"], 
                                          key=f"{key_prefix}_chart_discrepancias", horizontal=True)
                
                ia_errors = discrepancias_df['sugerencia_ia'].value_counts().rename("Sugerencia IA (Incorrecta)")
                human_corrections = discrepancias_df['nivel_corregido'].value_counts().rename("Corrección Humana")
                error_comparison_df = pd.concat([ia_errors, human_corrections], axis=1).fillna(0).astype(int)
                
                if chart_type_disc == "Barras Agrupadas":
                    st.bar_chart(error_comparison_df, use_container_width=True)
                elif chart_type_disc == "Barras Apiladas":
                    st.bar_chart(error_comparison_df, use_container_width=True, stack=True)
                else:
                    st.area_chart(error_comparison_df, use_container_width=True)
            
            with col_table:
                st.markdown("##### Detalle de Casos")
                st.dataframe(discrepancias_df[['timestamp', 'sugerencia_ia', 'nivel_corregido', 'justificacion_humana']], 
                           use_container_width=True, hide_index=True)
        else:
            st.success("✅ No se han encontrado discrepancias entre la IA y las decisiones humanas.")
