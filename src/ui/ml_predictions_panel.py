# path: src/ui/ml_predictions_panel.py
# Creado: 2025-11-26
"""
Panel de predicciones y análisis con Machine Learning.
"""
import streamlit as st
from datetime import datetime, timedelta, date
from services.ml_predictive_service import get_ml_service
from db.repositories.salas import get_all_salas
import pandas as pd

def render_ml_predictions_panel():
    """
    Renderiza el panel de predicciones ML.
    """
    st.markdown("### 🤖 Predicciones y Análisis IA")
    st.caption("Predicciones basadas en Machine Learning y análisis predictivo")
    
    ml_service = get_ml_service()
    
    st.markdown("### 🤖 Panel de Control ML")
    
    col_actions, col_status = st.columns([1, 1])
    
    with col_actions:
        if st.button("🔄 Re-entrenar Modelos", help="Entrenar modelos con datos actuales"):
            with st.spinner("Entrenando modelos Random Forest..."):
                from services.ml_training_service import MLTrainingService
                trainer = MLTrainingService()
                result = trainer.train_all()
                
                if result.get("status") == "success":
                    st.success(result.get("msg"))
                    # Recargar servicio de predicción
                    get_ml_service().load_models()
                else:
                    st.error(f"Error: {result.get('msg')}")
                    
    with col_status:
        service = get_ml_service()
        if service.models_loaded:
            st.success("✅ Modelos Activos (RandomForest)")
            st.caption("Predicciones basadas en datos históricos.")
        else:
            st.warning("⚠️ Modelos No Cargados")
            st.caption("Usando heurística de respaldo.")

    st.divider()

    tabs = st.tabs(["📊 Demanda", "⏱️ Tiempos de Espera", "👥 Staffing", "🔍 Anomalías"])
    
    with tabs[0]:
        render_demand_prediction_tab(ml_service)
    
    with tabs[1]:
        render_wait_time_tab(ml_service)
    
    with tabs[2]:
        render_staffing_recommendations_tab(ml_service)
    
    with tabs[3]:
        render_anomaly_detection_tab(ml_service)


def render_demand_prediction_tab(ml_service):
    """
    Tab de predicción de demanda.
    """
    st.subheader("Predicción de Demanda")
    
    # Selector de sala y fecha
    salas = get_all_salas()
    col1, col2 = st.columns(2)
    
    with col1:
        sala_options = {s['codigo']: f"{s['nombre']} ({s['codigo']})" for s in salas}
        selected_sala = st.selectbox(
            "Sala",
            options=list(sala_options.keys()),
            format_func=lambda x: sala_options[x]
        )
    
    with col2:
        fecha_pred = st.date_input("Fecha de Predicción", value=date.today() + timedelta(days=1))
    
    st.divider()
    
    # Generar predicciones para todo el día
    st.markdown("#### Predicción por Hora")
    
    predictions = []
    for hora in range(24):
        pred = ml_service.predict_demand(selected_sala, fecha_pred, hora)
        predictions.append({
            'Hora': f"{hora:02d}:00",
            'Demanda Predicha': pred['demanda_predicha'],
            'Mín': pred['intervalo_min'],
            'Máx': pred['intervalo_max']
        })
    
    df_pred = pd.DataFrame(predictions)
    
    # Gráfico
    st.line_chart(df_pred.set_index('Hora')['Demanda Predicha'])
    
    # Tabla detallada
    with st.expander("Ver Datos Detallados"):
        st.dataframe(df_pred, use_container_width=True, hide_index=True)
    
    # Resumen
    st.divider()
    st.markdown("#### Resumen del Día")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Demanda Máxima", df_pred['Demanda Predicha'].max())
    with col2:
        st.metric("Demanda Promedio", f"{df_pred['Demanda Predicha'].mean():.1f}")
    with col3:
        hora_pico = df_pred.loc[df_pred['Demanda Predicha'].idxmax(), 'Hora']
        st.metric("Hora Pico", hora_pico)


def render_wait_time_tab(ml_service):
    """
    Tab de predicción de tiempos de espera.
    """
    st.subheader("Predicción de Tiempos de Espera")
    
    # Simulador
    st.markdown("#### Simulador de Tiempo de Espera")
    
    col1, col2 = st.columns(2)
    
    with col1:
        salas = get_all_salas()
        sala_options = {s['codigo']: f"{s['nombre']} ({s['codigo']})" for s in salas}
        selected_sala = st.selectbox(
            "Sala",
            options=list(sala_options.keys()),
            format_func=lambda x: sala_options[x],
            key="wait_sala"
        )
    
    with col2:
        pacientes_espera = st.slider(
            "Pacientes en Espera",
            min_value=0,
            max_value=30,
            value=5
        )
    
    # Calcular predicción
    pred = ml_service.predict_wait_time(selected_sala, pacientes_espera)
    
    st.divider()
    
    # Mostrar resultado
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tiempo Predicho", f"{pred['tiempo_predicho_min']} min")
    
    with col2:
        st.metric("Tiempo por Paciente", f"{pred['tiempo_por_paciente']} min")
    
    with col3:
        nivel_color = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }[pred['nivel_carga']]
        st.metric("Nivel de Carga", f"{nivel_color} {pred['nivel_carga'].upper()}")
    
    # Gráfico de proyección
    st.divider()
    st.markdown("#### Proyección de Tiempos según Carga")
    
    cargas = list(range(0, 31, 5))
    tiempos = [ml_service.predict_wait_time(selected_sala, c)['tiempo_predicho_min'] for c in cargas]
    
    df_projection = pd.DataFrame({
        'Pacientes en Espera': cargas,
        'Tiempo Estimado (min)': tiempos
    })
    
    st.line_chart(df_projection.set_index('Pacientes en Espera'))


def render_staffing_recommendations_tab(ml_service):
    """
    Tab de recomendaciones de personal.
    """
    st.subheader("Recomendaciones de Personal")
    
    # Selector
    col1, col2 = st.columns(2)
    
    with col1:
        salas = get_all_salas()
        sala_options = {s['codigo']: f"{s['nombre']} ({s['codigo']})" for s in salas}
        selected_sala = st.selectbox(
            "Sala",
            options=list(sala_options.keys()),
            format_func=lambda x: sala_options[x],
            key="staff_sala"
        )
    
    with col2:
        fecha_staff = st.date_input("Fecha", value=date.today() + timedelta(days=1), key="staff_fecha")
    
    if st.button("🔍 Generar Recomendaciones", type="primary"):
        with st.spinner("Analizando patrones y generando recomendaciones..."):
            import time
            time.sleep(1)  # Simular procesamiento
            
            recom = ml_service.recommend_staffing(selected_sala, fecha_staff)
            
            st.success("✅ Recomendaciones generadas")
            
            st.divider()
            
            # Personal recomendado
            st.markdown("#### Personal Recomendado")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("👨‍⚕️ Médicos", recom['personal_recomendado']['medicos'])
            
            with col2:
                st.metric("👩‍⚕️ Enfermeros", recom['personal_recomendado']['enfermeros'])
            
            with col3:
                st.metric("👔 Administrativos", recom['personal_recomendado']['administrativos'])
            
            # Métricas de demanda
            st.divider()
            st.markdown("#### Análisis de Demanda")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Demanda Máxima Esperada", recom['demanda_maxima'])
            
            with col2:
                st.metric("Demanda Promedio", recom['demanda_promedio'])
            
            # Turnos recomendados
            st.divider()
            st.markdown("#### Turnos Recomendados")
            
            for turno in recom['turnos_recomendados']:
                prioridad_color = {
                    'alta': '🔴',
                    'media': '🟡',
                    'baja': '🟢'
                }[turno['prioridad']]
                
                with st.container(border=True):
                    col_info, col_staff = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**{turno['turno']}** - {turno['horario']}")
                        st.caption(f"Prioridad: {prioridad_color} {turno['prioridad'].upper()}")
                    
                    with col_staff:
                        st.metric("Personal", turno['personal_recomendado'])
            
            # Justificación
            st.divider()
            st.info(recom['justificacion'])


def render_anomaly_detection_tab(ml_service):
    """
    Tab de detección de anomalías.
    """
    st.subheader("Detección de Anomalías")
    
    # Selector
    col1, col2 = st.columns(2)
    
    with col1:
        salas = get_all_salas()
        sala_options = {s['codigo']: f"{s['nombre']} ({s['codigo']})" for s in salas}
        selected_sala = st.selectbox(
            "Sala",
            options=list(sala_options.keys()),
            format_func=lambda x: sala_options[x],
            key="anomaly_sala"
        )
    
    with col2:
        dias_historico = st.slider("Días de Histórico", min_value=7, max_value=90, value=30)
    
    if st.button("🔍 Detectar Anomalías", type="primary"):
        with st.spinner("Analizando patrones históricos..."):
            import time
            time.sleep(1)
            
            anomalies = ml_service.detect_anomalies(selected_sala, dias_historico)
            
            if not anomalies:
                st.success("✅ No se detectaron anomalías significativas")
            else:
                st.warning(f"⚠️ Se detectaron {len(anomalies)} anomalías")
                
                for anomaly in anomalies:
                    severity_color = {
                        'alta': 'error',
                        'media': 'warning',
                        'baja': 'info'
                    }[anomaly['severidad']]
                    
                    tipo_icon = '📈' if anomaly['tipo'] == 'pico_inusual' else '📉'
                    
                    with st.container(border=True):
                        col_date, col_data = st.columns([1, 3])
                        
                        with col_date:
                            st.markdown(f"**{anomaly['fecha'].strftime('%d/%m/%Y')}**")
                            st.caption(f"{tipo_icon} {anomaly['tipo'].replace('_', ' ').title()}")
                        
                        with col_data:
                            getattr(st, severity_color)(
                                f"Desviación de {anomaly['desviacion']} pacientes "
                                f"(Esperado: {anomaly['demanda_esperada']}, Real: {anomaly['demanda_real']})"
                            )

    st.markdown("---")
    st.caption(f"📍 `src/ui/ml_predictions_panel.py`")

# Footer de depuración
if __name__ == "__main__":
    render_ml_predictions_panel()
