import pandas as pd
import streamlit as st

def calculate_triage_quality_metrics(df: pd.DataFrame) -> dict:
    """
    Calcula métricas de calidad de triaje comparando la decisión humana vs IA.
    
    Args:
        df (pd.DataFrame): DataFrame con registros de auditoría.
                           Debe contener columnas 'decision_humana' y 'decision_ia' (o extraíbles de 'detalles').
    
    Returns:
        dict: Diccionario con métricas (total, match_rate, over_triage_rate, under_triage_rate).
    """
    metrics = {
        "total_validated": 0,
        "match_count": 0,
        "over_triage_count": 0,
        "under_triage_count": 0,
        "match_rate": 0.0,
        "over_triage_rate": 0.0,
        "under_triage_rate": 0.0
    }
    
    if df.empty:
        return metrics

    # Asegurar que tenemos las columnas necesarias
    # A veces la decisión IA está dentro de un objeto JSON en 'detalles' o columna separada
    # Asumiremos por ahora que el DF ya viene procesado o intentaremos extraerlo
    
    # Si no existen las columnas directas, intentar extraer de 'detalles' si es dict
    # Nota: Esto depende de cómo se construya el DF en `audit_service.py`
    
    # Filtrar solo registros que tengan ambas decisiones
    valid_records = df.copy()
    
    # Normalizar niveles (1 a 5)
    # Nivel 1 (Resucitación) < Nivel 5 (No Urgente)
    # Por tanto:
    # - Over-triage: IA (2) < Humano (4) -> IA asignó más urgencia
    # - Under-triage: IA (4) > Humano (2) -> IA asignó menos urgencia
    
    # Simulamos extracción si no existen columnas (ajustar según estructura real)
    if "nivel_ia" not in valid_records.columns and "detalles" in valid_records.columns:
        # Intentar extraer de detalles si es posible (esto es un placeholder, idealmente el repositorio ya lo trae)
        pass

    # Si no tenemos datos comparables, retornar vacío
    if "nivel_ia" not in valid_records.columns or "nivel_humano" not in valid_records.columns:
        return metrics

    # Filtrar nulos
    valid_records = valid_records.dropna(subset=["nivel_ia", "nivel_humano"])
    
    metrics["total_validated"] = len(valid_records)
    
    if metrics["total_validated"] == 0:
        return metrics

    # Calcular diferencias
    # Convertir a numérico por si acaso
    valid_records["nivel_ia"] = pd.to_numeric(valid_records["nivel_ia"], errors='coerce')
    valid_records["nivel_humano"] = pd.to_numeric(valid_records["nivel_humano"], errors='coerce')
    
    matches = valid_records[valid_records["nivel_ia"] == valid_records["nivel_humano"]]
    over_triage = valid_records[valid_records["nivel_ia"] < valid_records["nivel_humano"]] # Menor número = Mayor urgencia
    under_triage = valid_records[valid_records["nivel_ia"] > valid_records["nivel_humano"]] # Mayor número = Menor urgencia
    
    metrics["match_count"] = len(matches)
    metrics["over_triage_count"] = len(over_triage)
    metrics["under_triage_count"] = len(under_triage)
    
    metrics["match_rate"] = (metrics["match_count"] / metrics["total_validated"]) * 100
    metrics["over_triage_rate"] = (metrics["over_triage_count"] / metrics["total_validated"]) * 100
    metrics["under_triage_rate"] = (metrics["under_triage_count"] / metrics["total_validated"]) * 100
    
    return metrics

def render_quality_metrics_panel(metrics: dict):
    """Renderiza el panel visual de métricas."""
    if metrics["total_validated"] == 0:
        st.info("No hay suficientes datos validados para calcular métricas de calidad.")
        return

    st.markdown("#### 📊 Calidad del Triaje (IA vs Humano)")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("Registros Valid", metrics["total_validated"])
        
    with c2:
        st.metric("Coincidencia", f"{metrics['match_rate']:.1f}%", help="La IA y el humano coincidieron en el nivel.")
        
    with c3:
        st.metric("Sobre-triaje", f"{metrics['over_triage_rate']:.1f}%", delta_color="inverse", 
                 help="La IA asignó MAYOR urgencia (Nivel menor) que el humano. Objetivo < 50%")
        
    with c4:
        st.metric("Sub-triaje", f"{metrics['under_triage_rate']:.1f}%", delta_color="inverse",
                 help="La IA asignó MENOR urgencia (Nivel mayor) que el humano. CRÍTICO. Objetivo < 5%")

    # Progress bars visuales
    st.caption("Distribución de Validación")
    
    # Crear un dataframe para el gráfico de barras apiladas simple
    chart_data = pd.DataFrame({
        'Categoría': ['Coincidencia', 'Sobre-triaje', 'Sub-triaje'],
        'Porcentaje': [metrics['match_rate'], metrics['over_triage_rate'], metrics['under_triage_rate']]
    })
    
    st.bar_chart(chart_data, x="Categoría", y="Porcentaje", color=["#28a745", "#ffc107", "#dc3545"], horizontal=True, height=200)
