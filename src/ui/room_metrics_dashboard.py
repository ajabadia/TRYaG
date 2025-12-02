# path: src/ui/room_metrics_dashboard.py
# Creado: 2025-11-25
"""
Dashboard de métricas históricas de errores de asignación de salas.
"""
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from services.room_metrics_service import (
    obtener_metricas_errores,
    obtener_historial_errores,
    sync_errores_actuales,
    get_errors_time_series
)
from services.export_service import generate_metrics_pdf, generate_excel_export



def render_metrics_dashboard():
    """Renderiza el dashboard de métricas de errores de salas."""
    
    st.header("📈 Dashboard de Métricas - Gestión de Salas")
    st.markdown("Análisis histórico de errores detectados y correcciones aplicadas.")
    
    # Sincronizar errores actuales
    col_sync, col_period = st.columns([3, 1])
    
    with col_sync:
        if st.button("🔄 Sincronizar Errores Actuales", help="Registra los errores detectados ahora en el sistema de tracking"):
            with st.spinner("Sincronizando..."):
                nuevos = sync_errores_actuales()
                if nuevos > 0:
                    st.success(f"✅ Se registraron {nuevos} nuevo(s) error(es)")
                else:
                    st.info("ℹ️ No hay errores nuevos para registrar")
    
    with col_period:
        periodo = st.selectbox(
            "Periodo",
            options=[7, 14, 30, 90],
            format_func=lambda x: f"Últimos {x} días",
            index=0
        )
    
    # Botones de Exportación
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if st.button("📄 Exportar Reporte PDF", use_container_width=True):
            try:
                pdf_bytes = generate_metrics_pdf(periodo_dias=periodo)
                st.download_button(
                    "⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"reporte_salas_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generando PDF: {e}")
                
    with col_exp2:
        if st.button("📊 Exportar Datos Excel", use_container_width=True):
            try:
                excel_bytes = generate_excel_export(periodo_dias=periodo)
                st.download_button(
                    "⬇️ Descargar Excel",
                    data=excel_bytes,
                    file_name=f"datos_salas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generando Excel: {e}")
    
    # Cargar métricas
    metricas = obtener_metricas_errores(dias=periodo)
    
    st.markdown("---")
    
    # KPIs principales
    st.markdown("### 📊 Indicadores Clave")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Errores",
            metricas["total_errores"],
            help=f"Errores detectados en los últimos {periodo} días"
        )
    
    with col2:
        delta_color = "normal" if metricas["tasa_resolucion"] >= 80 else "inverse"
        st.metric(
            "Tasa Resolución",
            f"{metricas['tasa_resolucion']}%",
            delta=None,
            delta_color=delta_color,
            help="Porcentaje de errores resueltos"
        )
    
    with col3:
        st.metric(
            "⚠️ Pendientes",
            metricas["pendientes"],
            delta=None,
            delta_color="inverse" if metricas["pendientes"] > 0 else "normal",
            help="Errores aún sin resolver"
        )
    
    with col4:
        st.metric(
            "⏱️ Tiempo Promedio",
            f"{metricas['tiempo_promedio_minutos']} min",
            help="Tiempo promedio de resolución"
        )
    
    st.markdown("---")
    
    # Gráfico de Evolución Temporal (Time Series)
    st.markdown("### 📈 Evolución Temporal")
    render_time_series_chart(periodo)
    
    st.markdown("---")
    
    # Gráficos de distribución
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### Errores por Motivo")
        
        if metricas["por_motivo"]:
            motivos = list(metricas["por_motivo"].keys())
            valores = list(metricas["por_motivo"].values())
            
            fig_motivo = go.Figure(data=[
                go.Pie(
                    labels=motivos,
                    values=valores,
                    hole=0.4,
                    marker=dict(colors=['#FF6B6B', '#FFA500'])
                )
            ])
            
            fig_motivo.update_layout(
                showlegend=True,
                height=300,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig_motivo, use_container_width=True)
        else:
            st.info("No hay datos para mostrar")
    
    with col_chart2:
        st.markdown("#### Tipo de Resolución")
        
        if metricas["por_resolucion"]:
            tipos = list(metricas["por_resolucion"].keys())
            valores = list(metricas["por_resolucion"].values())
            
            # Mapear nombres amigables
            nombres_amigables = {
                "reasignado": "Reasignado",
                "rechazado": "Rechazado/Alta",
                "auto_corregido": "Auto-corregido"
            }
            tipos_friendly = [nombres_amigables.get(t, t) for t in tipos]
            
            fig_resolucion = go.Figure(data=[
                go.Bar(
                    x=tipos_friendly,
                    y=valores,
                    marker=dict(color=['#4CAF50', '#2196F3', '#9C27B0'])
                )
            ])
            
            fig_resolucion.update_layout(
                showlegend=False,
                height=300,
                margin=dict(t=20, b=20, l=20, r=20),
                yaxis_title="Cantidad"
            )
            
            st.plotly_chart(fig_resolucion, use_container_width=True)
        else:
            st.info("No hay resoluciones registradas")
    
    st.markdown("---")
    
    # Historial de errores
    st.markdown("### 📋 Historial de Errores")
    
    tab_pending, tab_all = st.tabs(["⚠️ Pendientes", "📚 Todos"])
    
    with tab_pending:
        errores_pendientes = obtener_historial_errores(limit=50, solo_pendientes=True)
        
        if errores_pendientes:
            st.caption(f"Se encontraron {len(errores_pendientes)} error(es) pendiente(s)")
            
            for error in errores_pendientes:
                with st.container(border=True):
                    col_info, col_meta = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**{error.get('nombre_completo', 'N/A')}** `{error.get('patient_code', 'N/A')}`")
                        
                        if error.get('motivo_error') == "Sala inexistente":
                            st.error(f"🚫 Sala **{error.get('sala_erronea')}** no existe")
                        else:
                            st.warning(f"⚠️ Sala **{error.get('sala_erronea')}** inactiva")
                        
                        st.caption(f"Estado: {error.get('estado', 'N/A')}")
                    
                    with col_meta:
                        detected_at = error.get('detected_at')
                        if detected_at:
                            tiempo_transcurrido = datetime.now() - detected_at
                            horas = int(tiempo_transcurrido.total_seconds() / 3600)
                            st.metric("Tiempo", f"{horas}h")
                            st.caption(detected_at.strftime("%d/%m %H:%M"))
        else:
            st.success("✅ No hay errores pendientes")
    
    with tab_all:
        todos_errores = obtener_historial_errores(limit=100, solo_pendientes=False)
        
        if todos_errores:
            st.caption(f"Mostrando últimos {len(todos_errores)} errores registrados")
            
            # Convertir a tabla
            tabla_data = []
            for error in todos_errores:
                tabla_data.append({
                    "Fecha": error.get('detected_at', datetime.now()).strftime("%d/%m/%Y %H:%M"),
                    "Paciente": error.get('nombre_completo', 'N/A'),
                    "ID": error.get('patient_code', 'N/A'),
                    "Sala": error.get('sala_erronea', 'N/A'),
                    "Motivo": error.get('motivo_error', 'N/A'),
                    "Estado": "✅ Resuelto" if error.get('resolved') else "⚠️ Pendiente",
                    "Solución": error.get('resolution_type', '-') if error.get('resolved') else '-'
                })
            
            st.dataframe(
                tabla_data,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay errores registrados en el sistema")
    
    st.markdown("---")
    st.caption("💡 **Consejo:** Usa 'Sincronizar Errores Actuales' regularmente para mantener el tracking actualizado.")
    
    # -----------------------------------------------------------------------
    # Programación de Reportes
    # -----------------------------------------------------------------------
    from db.repositories.report_config import get_report_config, save_report_config
    from services.scheduled_reports import reload_scheduler
    
    st.markdown("### 📅 Programación de Reportes Automáticos")
    
    with st.expander("Configurar Reporte Semanal", expanded=False):
        config = get_report_config()
        
        with st.form("report_schedule_form"):
            enabled = st.checkbox("Habilitar envío automático", value=config.get("enabled", False))
            
            col_sched1, col_sched2 = st.columns(2)
            with col_sched1:
                day = st.selectbox(
                    "Día de la semana",
                    options=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                    index=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(config.get("day_of_week", "monday")),
                    format_func=lambda x: x.capitalize()
                )
            with col_sched2:
                time_str = st.text_input("Hora (HH:MM)", value=config.get("time", "08:00"))
            
            recipients_str = st.text_area(
                "Destinatarios (separados por coma)",
                value=", ".join(config.get("recipients", [])),
                help="Ej: admin@hospital.com, director@hospital.com"
            )
            
            if st.form_submit_button("💾 Guardar Programación"):
                recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
                save_report_config(recipients, day, time_str, enabled)
                reload_scheduler()
                st.success("Programación actualizada correctamente")
                st.rerun()


def render_time_series_chart(periodo_dias: int = 30):
    """Gráfico de línea con evolución temporal de errores"""
    
    # Obtener datos agrupados por día
    errors_by_day = get_errors_time_series(periodo_dias)
    
    if not errors_by_day['fecha']:
        st.info("No hay datos suficientes para mostrar la evolución temporal.")
        return

    fig = go.Figure()
    
    # Línea de errores totales
    fig.add_trace(go.Scatter(
        x=errors_by_day['fecha'],
        y=errors_by_day['total'],
        name='Total Errores',
        mode='lines+markers',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    
    # Línea de errores resueltos
    fig.add_trace(go.Scatter(
        x=errors_by_day['fecha'],
        y=errors_by_day['resueltos'],
        name='Resueltos',
        mode='lines+markers',
        line=dict(color='#4CAF50', width=3, dash='dot'),
        marker=dict(size=8, symbol='diamond')
    ))
    
    fig.update_layout(
        title=dict(
            text='Evolución Diaria de Errores',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Fecha',
        yaxis_title='Cantidad de Errores',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
