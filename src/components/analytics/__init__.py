# path: src/components/analytics/__init__.py
"""
Componentes modulares para análisis gráfico.
"""
from .kpis import render_kpis
from .evolution import render_evolution
from .triage_analysis import render_triage_analysis
from .file_analysis import render_file_analysis
from .transcription_analysis import render_transcription_analysis
from .relational_analysis import render_relational_analysis

__all__ = [
    'render_kpis',
    'render_evolution',
    'render_triage_analysis',
    'render_file_analysis',
    'render_transcription_analysis',
    'render_relational_analysis'
]
