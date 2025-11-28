# path: src/components/admission/__init__.py
# Creado: 2025-11-24
"""
Módulo de componentes para el flujo de admisión de pacientes.
"""
from .step_sala_admision import render_step_sala_admision
from .step_patient_data import render_step_patient_data
from .step_sala_triaje import render_step_sala_triaje
from .step_confirmation import render_step_confirmation

__all__ = [
    'render_step_sala_admision',
    'render_step_patient_data',
    'render_step_sala_triaje',
    'render_step_confirmation',
]
