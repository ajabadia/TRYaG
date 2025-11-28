# path: src/ui/multi_center_dashboard.py
# Creado: 2025-11-26
"""
Dashboard de administración global para gestión multi-centro.
Permite vista consolidada de múltiples centros y comparativas.
"""
import streamlit as st
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
import pandas as pd

def render_multi_center_dashboard():
    """
    Renderiza el dashboard global multi-centro.
    """
    st.markdown("### 🏥 Dashboard Multi-Centro")
    st.caption("Vista consolidada de todos los centros de la red")
    
    # Selector de centros (simulado - en producción vendría de BD)
    centros_disponibles = _get_available_centers()
    
    selected_centers = st.multiselect(
        "Centros a Visualizar",
        options=[c['id'] for c in centros_disponibles],
        default=[c['id'] for c in centros_disponibles[:3]],
        format_func=lambda x: next(c['nombre'] for c in centros_disponibles if c['id'] == x)
    )
    
    if not selected_centers:
        st.warning("Selecciona al menos un centro para visualizar")
        return
    
    st.divider()
    
    # Tabs principales
    tabs = st.tabs([
        "📊 Vista General",
        "📈 Comparativas",
        "🚨 Alertas Globales",
        "📋 Reportes Consolidados"
    ])
    
    with tabs[0]:
        render_overview_tab(selected_centers, centros_disponibles)
    
    with tabs[1]:
        render_comparative_tab(selected_centers, centros_disponibles)
    
    with tabs[2]:
        render_global_alerts_tab(selected_centers, centros_disponibles)
    
    with tabs[3]:
        render_consolidated_reports_tab(selected_centers, centros_disponibles)


def _get_available_centers() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de centros disponibles.
    En producción, esto vendría de una base de datos.
    """
    return [
        {
            'id': 'centro_001',
            'nombre': 'Hospital Central',
            'ciudad': 'Madrid',
            'tipo': 'Hospital General',
            'capacidad': 500
        },
        {
            'id': 'centro_002',
            'nombre': 'Hospital Norte',
            'ciudad': 'Barcelona',
            'tipo': 'Hospital General',
            'capacidad': 350
        },
        {
            'id': 'centro_003',
            'nombre': 'Centro Urgencias Sur',
            'ciudad': 'Valencia',
            'tipo': 'Centro de Urgencias',
            'capacidad': 150
        },
        {
            'id': 'centro_004',
            'nombre': 'Hospital Universitario',
            'ciudad': 'Sevilla',
            'tipo': 'Hospital Universitario',
            'capacidad': 600
        }
    ]


def render_overview_tab(selected_centers, all_centers):
    """
    Vista general con KPIs de todos los centros.
    """
    st.subheader("Vista General")
    
    # KPIs globales
    col1, col2, col3, col4 = st.columns(4)
    
    # Datos simulados - en producción vendrían de servicios reales
    total_pacientes = sum(_get_center_patients(c) for c in selected_centers)
    total_salas = sum(_get_center_rooms(c) for c in selected_centers)
    avg_wait_time = sum(_get_center_avg_wait(c) for c in selected_centers) / len(selected_centers)
    total_staff = sum(_get_center_staff(c) for c in selected_centers)
    
    with col1:
        st.metric("Pacientes Totales", total_pacientes, delta="+12 vs ayer")
    with col2:
        st.metric("Salas Activas", total_salas)
    with col3:
        st.metric("Tiempo Espera Promedio", f"{avg_wait_time:.0f} min", delta="-5 min")
    with col4:
        st.metric("Personal Total", total_staff)
    
    st.divider()
    
    # Tabla de centros
    st.markdown("#### Estado por Centro")
    
    data = []
    for center_id in selected_centers:
        center = next(c for c in all_centers if c['id'] == center_id)
        data.append({
            'Centro': center['nombre'],
            'Ciudad': center['ciudad'],
            'Pacientes': _get_center_patients(center_id),
            'Ocupación': f"{_get_center_occupancy(center_id):.0f}%",
            'Espera (min)': _get_center_avg_wait(center_id),
            'Estado': _get_center_status(center_id)
        })
    
    df = pd.DataFrame(data)
    
    # Aplicar estilos
    def highlight_status(row):
        if row['Estado'] == '🟢 Normal':
            return ['background-color: #d4edda'] * len(row)
        elif row['Estado'] == '🟡 Alerta':
            return ['background-color: #fff3cd'] * len(row)
        else:
            return ['background-color: #f8d7da'] * len(row)
    
    st.dataframe(
        df.style.apply(highlight_status, axis=1),
        use_container_width=True,
        hide_index=True
    )


def render_comparative_tab(selected_centers, all_centers):
    """
    Comparativas entre centros.
    """
    st.subheader("Análisis Comparativo")
    
    # Gráfico de barras comparativo
    st.markdown("#### Pacientes por Centro")
    
    data = {
        'Centro': [next(c['nombre'] for c in all_centers if c['id'] == cid) for cid in selected_centers],
        'Pacientes': [_get_center_patients(cid) for cid in selected_centers]
    }
    df = pd.DataFrame(data)
    st.bar_chart(df.set_index('Centro'))
    
    st.divider()
    
    # Comparativa de tiempos de espera
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Tiempo de Espera")
        data = {
            'Centro': [next(c['nombre'] for c in all_centers if c['id'] == cid) for cid in selected_centers],
            'Minutos': [_get_center_avg_wait(cid) for cid in selected_centers]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index('Centro'))
    
    with col2:
        st.markdown("#### Ocupación (%)")
        data = {
            'Centro': [next(c['nombre'] for c in all_centers if c['id'] == cid) for cid in selected_centers],
            'Ocupación': [_get_center_occupancy(cid) for cid in selected_centers]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index('Centro'))
    
    st.divider()
    
    # Ranking de centros
    st.markdown("#### Ranking de Eficiencia")
    
    ranking_data = []
    for center_id in selected_centers:
        center = next(c for c in all_centers if c['id'] == center_id)
        efficiency_score = _calculate_efficiency_score(center_id)
        ranking_data.append({
            'Centro': center['nombre'],
            'Puntuación': efficiency_score,
            'Pacientes/Hora': _get_center_patients(center_id) / 8,  # Simulado
            'Satisfacción': f"{_get_center_satisfaction(center_id):.1f}/5.0"
        })
    
    df_ranking = pd.DataFrame(ranking_data).sort_values('Puntuación', ascending=False)
    st.dataframe(df_ranking, use_container_width=True, hide_index=True)


def render_global_alerts_tab(selected_centers, all_centers):
    """
    Alertas globales de todos los centros.
    """
    st.subheader("Alertas Globales")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        severity_filter = st.multiselect(
            "Severidad",
            ["🔴 Crítica", "🟡 Media", "🟢 Baja"],
            default=["🔴 Crítica", "🟡 Media"]
        )
    with col2:
        type_filter = st.multiselect(
            "Tipo",
            ["Ocupación", "Espera", "Personal", "Sistema"],
            default=["Ocupación", "Espera", "Personal"]
        )
    
    st.divider()
    
    # Generar alertas (simuladas)
    alerts = _get_global_alerts(selected_centers, all_centers)
    
    # Filtrar
    filtered_alerts = [
        a for a in alerts
        if a['severity'] in severity_filter and a['type'] in type_filter
    ]
    
    if not filtered_alerts:
        st.success("✅ No hay alertas activas con los filtros seleccionados")
    else:
        st.warning(f"⚠️ {len(filtered_alerts)} alertas activas")
        
        for alert in filtered_alerts:
            severity_color = {
                '🔴 Crítica': 'error',
                '🟡 Media': 'warning',
                '🟢 Baja': 'info'
            }[alert['severity']]
            
            with st.container(border=True):
                col_info, col_action = st.columns([4, 1])
                
                with col_info:
                    getattr(st, severity_color)(
                        f"{alert['severity']} - {alert['center']} - {alert['type']}"
                    )
                    st.caption(alert['message'])
                    st.caption(f"🕐 {alert['timestamp'].strftime('%H:%M:%S')}")
                
                with col_action:
                    if st.button("Ver", key=f"alert_{alert['id']}"):
                        st.info(f"Redirigiendo a {alert['center']}...")


def render_consolidated_reports_tab(selected_centers, all_centers):
    """
    Reportes consolidados multi-centro.
    """
    st.subheader("Reportes Consolidados")
    
    # Período de reporte
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=date.today() - timedelta(days=7))
    with col2:
        fecha_fin = st.date_input("Hasta", value=date.today())
    
    st.divider()
    
    # Tipo de reporte
    report_type = st.selectbox(
        "Tipo de Reporte",
        [
            "Resumen Ejecutivo",
            "Análisis de Flujo de Pacientes",
            "Utilización de Recursos",
            "Indicadores de Calidad"
        ]
    )
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        with st.spinner("Generando reporte..."):
            # Simular generación
            import time
            time.sleep(1)
            
            st.success("✅ Reporte generado")
            
            # Mostrar resumen
            st.markdown(f"### {report_type}")
            st.markdown(f"**Período:** {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
            st.markdown(f"**Centros incluidos:** {len(selected_centers)}")
            
            # Datos de ejemplo
            summary_data = {
                'Métrica': [
                    'Total Pacientes Atendidos',
                    'Tiempo Espera Promedio',
                    'Tasa de Ocupación',
                    'Satisfacción del Paciente'
                ],
                'Valor': ['1,234', '45 min', '78%', '4.2/5.0'],
                'Variación': ['+8%', '-12%', '+3%', '+0.2']
            }
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
            # Botón de descarga
            st.download_button(
                "📥 Descargar Reporte (PDF)",
                data="Reporte simulado",
                file_name=f"reporte_{fecha_inicio}_{fecha_fin}.pdf",
                mime="application/pdf"
            )


# Funciones helper para datos simulados
def _get_center_patients(center_id: str) -> int:
    """Obtiene número de pacientes (simulado)."""
    import random
    random.seed(hash(center_id))
    return random.randint(20, 100)

def _get_center_rooms(center_id: str) -> int:
    """Obtiene número de salas (simulado)."""
    import random
    random.seed(hash(center_id))
    return random.randint(10, 30)

def _get_center_avg_wait(center_id: str) -> float:
    """Obtiene tiempo de espera promedio (simulado)."""
    import random
    random.seed(hash(center_id))
    return random.uniform(20, 90)

def _get_center_staff(center_id: str) -> int:
    """Obtiene número de personal (simulado)."""
    import random
    random.seed(hash(center_id))
    return random.randint(15, 50)

def _get_center_occupancy(center_id: str) -> float:
    """Obtiene ocupación (simulado)."""
    import random
    random.seed(hash(center_id))
    return random.uniform(50, 95)

def _get_center_status(center_id: str) -> str:
    """Obtiene estado del centro (simulado)."""
    occupancy = _get_center_occupancy(center_id)
    if occupancy > 85:
        return '🔴 Saturado'
    elif occupancy > 70:
        return '🟡 Alerta'
    else:
        return '🟢 Normal'

def _get_center_satisfaction(center_id: str) -> float:
    """Obtiene satisfacción (simulado)."""
    import random
    random.seed(hash(center_id))
    return random.uniform(3.5, 5.0)

def _calculate_efficiency_score(center_id: str) -> float:
    """Calcula puntuación de eficiencia (simulado)."""
    import random
    random.seed(hash(center_id))
    return random.uniform(70, 95)

def _get_global_alerts(selected_centers, all_centers) -> List[Dict]:
    """Genera alertas globales (simuladas)."""
    alerts = []
    
    for center_id in selected_centers:
        center = next(c for c in all_centers if c['id'] == center_id)
        occupancy = _get_center_occupancy(center_id)
        
        if occupancy > 85:
            alerts.append({
                'id': f"{center_id}_occupancy",
                'center': center['nombre'],
                'severity': '🔴 Crítica',
                'type': 'Ocupación',
                'message': f"Ocupación al {occupancy:.0f}% - Considerar derivaciones",
                'timestamp': datetime.now()
            })
        
        wait_time = _get_center_avg_wait(center_id)
        if wait_time > 60:
            alerts.append({
                'id': f"{center_id}_wait",
                'center': center['nombre'],
                'severity': '🟡 Media',
                'type': 'Espera',
                'message': f"Tiempo de espera elevado: {wait_time:.0f} minutos",
                'timestamp': datetime.now()
            })
    
    return alerts
