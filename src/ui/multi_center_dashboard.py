# path: src/ui/multi_center_dashboard.py
# Creado: 2025-11-26
# Actualizado: 2025-12-02 (Real Data Integration)
"""
Dashboard de administración global para gestión multi-centro.
Permite vista consolidada de múltiples centros y comparativas.
"""
import streamlit as st
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
import pandas as pd
from services.multi_center_service import get_multi_center_service

def render_multi_center_dashboard():
    """
    Renderiza el dashboard global multi-centro.
    """
    service = get_multi_center_service()
    
    st.markdown("### 🏥 Dashboard Multi-Centro")
    st.caption("Vista consolidada de todos los centros de la red (Datos Reales)")
    
    # Obtener centros reales
    centros_disponibles = service.get_available_centers()
    
    if not centros_disponibles:
        st.warning("No se encontraron centros configurados en el sistema.")
        st.info("Mostrando datos de demostración para visualización.")
        # Fallback a demo si no hay datos
        centros_disponibles = _get_demo_centers()

    # --- FILTRO POR GRUPO ---
    from db.repositories.center_groups import get_center_group_repository
    group_repo = get_center_group_repository()
    groups = group_repo.get_all()
    
    selected_group_id = None
    if groups:
        group_options = ["Todos"] + [g.name for g in groups]
        selected_group_name = st.selectbox("Filtrar por Grupo", group_options)
        
        if selected_group_name != "Todos":
            selected_group = next((g for g in groups if g.name == selected_group_name), None)
            if selected_group:
                selected_group_id = str(selected_group.id)
                # Filtrar centros disponibles si tienen ID
                # Nota: centros_disponibles puede ser dicts o objetos, y los IDs pueden ser str o ObjectId
                # Asumimos que center_ids en grupo son strings que coinciden con el ID del centro
                
                # Normalizar IDs de centros disponibles para comparación
                centers_in_group = []
                for c in centros_disponibles:
                    c_id = str(c.get('id', c.get('_id')))
                    if c_id in selected_group.center_ids:
                        centers_in_group.append(c)
                
                # Si encontramos coincidencias, filtramos. Si no (ej: demo data), no filtramos pero avisamos.
                if centers_in_group:
                    centros_disponibles = centers_in_group
                elif not selected_group.center_ids:
                    st.warning(f"El grupo '{selected_group_name}' no tiene centros asignados.")
                else:
                    # Caso donde hay IDs pero no coinciden (ej: datos demo vs grupos reales)
                    pass

    selected_centers = st.multiselect(
        "Centros a Visualizar",
        options=[c.get('id', c.get('_id')) for c in centros_disponibles], # Manejar _id de mongo o id simulado
        default=[c.get('id', c.get('_id')) for c in centros_disponibles], # Default: Todos los filtrados
        format_func=lambda x: next((c.get('nombre', 'Desconocido') for c in centros_disponibles if str(c.get('id', c.get('_id'))) == str(x)), x)
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
        render_overview_tab(selected_centers, centros_disponibles, service)
    
    with tabs[1]:
        render_comparative_tab(selected_centers, centros_disponibles, service)
    
    with tabs[2]:
        render_global_alerts_tab(selected_centers, centros_disponibles, service)
    
    with tabs[3]:
        render_consolidated_reports_tab(selected_centers, centros_disponibles)


def _get_demo_centers() -> List[Dict[str, Any]]:
    """Datos de fallback para demostración."""
    return [
        {'id': 'demo_001', 'nombre': 'Hospital Demo Central', 'ciudad': 'Madrid', 'tipo': 'Hospital', 'capacidad': 500},
        {'id': 'demo_002', 'nombre': 'Clínica Demo Norte', 'ciudad': 'Barcelona', 'tipo': 'Clínica', 'capacidad': 200}
    ]

def render_overview_tab(selected_centers, all_centers, service):
    """
    Vista general con KPIs de todos los centros.
    """
    st.subheader("Vista General")
    
    # KPIs globales reales
    kpis = service.get_global_kpis(selected_centers)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pacientes Totales", kpis.get('total_pacientes', 0))
    with col2:
        st.metric("Salas Activas", kpis.get('total_salas', 0))
    with col3:
        st.metric("Tiempo Espera Promedio", f"{kpis.get('avg_wait_time', 0)} min")
    with col4:
        st.metric("Personal Total", kpis.get('total_staff', 0))
    
    st.divider()
    
    # Tabla de centros
    st.markdown("#### Estado por Centro")
    
    data = []
    for center_id in selected_centers:
        # Encontrar centro (manejo robusto de ID)
        center = next((c for c in all_centers if c.get('id', c.get('_id')) == center_id), None)
        if not center: continue
            
        metrics = service.get_center_metrics(center_id)
        
        # Determinar estado basado en ocupación
        ocupacion = metrics.get('ocupacion', 0)
        if ocupacion > 85: estado = '🔴 Saturado'
        elif ocupacion > 70: estado = '🟡 Alerta'
        else: estado = '🟢 Normal'

        data.append({
            'Centro': center.get('nombre', 'N/A'),
            'Ciudad': center.get('ciudad', 'N/A'),
            'Pacientes': metrics.get('pacientes_activos', 0),
            'Ocupación': f"{ocupacion:.0f}%",
            'Capacidad': metrics.get('capacidad_total', 0),
            'Estado': estado
        })
    
    if data:
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
    else:
        st.info("No hay datos detallados disponibles.")


def render_comparative_tab(selected_centers, all_centers, service):
    """
    Comparativas entre centros.
    """
    st.subheader("Análisis Comparativo")
    
    data_list = []
    for cid in selected_centers:
        center = next((c for c in all_centers if c.get('id', c.get('_id')) == cid), None)
        if not center: continue
        
        metrics = service.get_center_metrics(cid)
        data_list.append({
            'Centro': center.get('nombre'),
            'Pacientes': metrics.get('pacientes_activos', 0),
            'Ocupación': metrics.get('ocupacion', 0)
        })
        
    if not data_list:
        st.info("No hay datos para comparar.")
        return

    df = pd.DataFrame(data_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Pacientes por Centro")
        st.bar_chart(df.set_index('Centro')['Pacientes'])
    
    with col2:
        st.markdown("#### Ocupación (%)")
        st.bar_chart(df.set_index('Centro')['Ocupación'])


def render_global_alerts_tab(selected_centers, all_centers, service):
    """
    Alertas globales basadas en datos reales.
    """
    st.subheader("Alertas Globales")
    
    alerts = []
    for cid in selected_centers:
        center = next((c for c in all_centers if c.get('id', c.get('_id')) == cid), None)
        if not center: continue
        
        metrics = service.get_center_metrics(cid)
        ocupacion = metrics.get('ocupacion', 0)
        
        if ocupacion > 85:
            alerts.append({
                'severity': '🔴 Crítica',
                'center': center.get('nombre'),
                'message': f"Ocupación crítica ({ocupacion:.0f}%)"
            })
        elif ocupacion > 70:
            alerts.append({
                'severity': '🟡 Media',
                'center': center.get('nombre'),
                'message': f"Ocupación elevada ({ocupacion:.0f}%)"
            })
            
    if not alerts:
        st.success("✅ No hay alertas activas en la red.")
    else:
        for alert in alerts:
             severity_color = 'error' if 'Crítica' in alert['severity'] else 'warning'
             getattr(st, severity_color)(f"{alert['severity']} - {alert['center']}: {alert['message']}")

def render_consolidated_reports_tab(selected_centers, all_centers):
    """
    Reportes consolidados (Placeholder por ahora).
    """
    st.subheader("Reportes Consolidados")
    st.info("Funcionalidad de generación de reportes PDF en desarrollo.")


    st.markdown('<div class="debug-footer">src/ui/multi_center_dashboard.py</div>', unsafe_allow_html=True)
