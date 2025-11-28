# path: src/services/ml_predictive_service.py
# Creado: 2025-11-26
"""
Servicio de Machine Learning para predicciones y optimizaciones.
Incluye predicción de demanda, tiempos de espera y recomendaciones de staffing.
"""
import streamlit as st
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np

class MLPredictiveService:
    """
    Servicio de predicciones con Machine Learning.
    Nota: Esta es una implementación básica con modelos estadísticos simples.
    En producción se usarían modelos entrenados con datos históricos reales.
    """
    
    def __init__(self):
        self.models_loaded = False
    
    def predict_demand(self, sala_code: str, fecha: date, hora: int) -> Dict[str, Any]:
        """
        Predice la demanda esperada para una sala en una fecha/hora específica.
        
        Args:
            sala_code: Código de la sala
            fecha: Fecha de predicción
            hora: Hora del día (0-23)
        
        Returns:
            Dict con predicción y confianza
        """
        # Modelo simple basado en patrones históricos simulados
        # En producción: usar modelo entrenado (RandomForest, XGBoost, etc.)
        
        # Factores que afectan la demanda
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
        es_fin_semana = dia_semana >= 5
        es_hora_pico = 10 <= hora <= 14 or 18 <= hora <= 21
        
        # Demanda base
        demanda_base = 15
        
        # Ajustes
        if es_fin_semana:
            demanda_base *= 0.7  # Menos demanda en fin de semana
        
        if es_hora_pico:
            demanda_base *= 1.5  # Más demanda en horas pico
        
        # Variación aleatoria (simula incertidumbre)
        variacion = np.random.normal(0, 2)
        demanda_predicha = max(0, demanda_base + variacion)
        
        # Calcular intervalo de confianza
        confianza = 0.85  # 85% de confianza
        margen_error = demanda_predicha * 0.15
        
        return {
            'demanda_predicha': round(demanda_predicha),
            'confianza': confianza,
            'intervalo_min': round(demanda_predicha - margen_error),
            'intervalo_max': round(demanda_predicha + margen_error),
            'factores': {
                'dia_semana': dia_semana,
                'es_fin_semana': es_fin_semana,
                'es_hora_pico': es_hora_pico
            }
        }
    
    def predict_wait_time(self, sala_code: str, pacientes_actuales: int) -> Dict[str, Any]:
        """
        Predice el tiempo de espera basado en pacientes actuales.
        
        Args:
            sala_code: Código de la sala
            pacientes_actuales: Número de pacientes en espera
        
        Returns:
            Dict con predicción de tiempo de espera
        """
        # Modelo simple: tiempo promedio por paciente
        tiempo_por_paciente = 15  # minutos (simulado)
        
        # Ajustar según carga
        if pacientes_actuales > 10:
            tiempo_por_paciente *= 1.2  # Más lento cuando hay sobrecarga
        
        tiempo_predicho = pacientes_actuales * tiempo_por_paciente
        
        return {
            'tiempo_predicho_min': round(tiempo_predicho),
            'pacientes_en_espera': pacientes_actuales,
            'tiempo_por_paciente': tiempo_por_paciente,
            'nivel_carga': self._get_load_level(pacientes_actuales)
        }
    
    def recommend_staffing(self, sala_code: str, fecha: date) -> Dict[str, Any]:
        """
        Recomienda el staffing óptimo para una sala en una fecha.
        
        Args:
            sala_code: Código de la sala
            fecha: Fecha para la recomendación
        
        Returns:
            Dict con recomendaciones de personal
        """
        # Predecir demanda para diferentes horas del día
        demandas_dia = []
        for hora in range(24):
            pred = self.predict_demand(sala_code, fecha, hora)
            demandas_dia.append(pred['demanda_predicha'])
        
        # Calcular picos de demanda
        demanda_max = max(demandas_dia)
        demanda_promedio = np.mean(demandas_dia)
        
        # Recomendar personal (regla simple: 1 persona cada 5 pacientes)
        personal_recomendado = {
            'medicos': max(1, round(demanda_max / 10)),
            'enfermeros': max(2, round(demanda_max / 5)),
            'administrativos': max(1, round(demanda_max / 15))
        }
        
        # Turnos recomendados
        turnos_recomendados = self._recommend_shifts(demandas_dia)
        
        return {
            'personal_recomendado': personal_recomendado,
            'demanda_maxima': round(demanda_max),
            'demanda_promedio': round(demanda_promedio),
            'turnos_recomendados': turnos_recomendados,
            'justificacion': self._generate_staffing_justification(demandas_dia)
        }
    
    def detect_anomalies(self, sala_code: str, dias_historico: int = 30) -> List[Dict[str, Any]]:
        """
        Detecta anomalías en patrones de uso de sala.
        
        Args:
            sala_code: Código de la sala
            dias_historico: Días de histórico a analizar
        
        Returns:
            Lista de anomalías detectadas
        """
        # Simular datos históricos
        anomalies = []
        
        # Ejemplo: Detectar picos inusuales
        for i in range(dias_historico):
            fecha = date.today() - timedelta(days=i)
            demanda_esperada = 15
            demanda_real = np.random.normal(15, 3)
            
            # Si la demanda real es muy diferente de la esperada
            if abs(demanda_real - demanda_esperada) > 10:
                anomalies.append({
                    'fecha': fecha,
                    'tipo': 'pico_inusual' if demanda_real > demanda_esperada else 'baja_inusual',
                    'demanda_esperada': round(demanda_esperada),
                    'demanda_real': round(demanda_real),
                    'desviacion': round(abs(demanda_real - demanda_esperada)),
                    'severidad': 'alta' if abs(demanda_real - demanda_esperada) > 15 else 'media'
                })
        
        return sorted(anomalies, key=lambda x: x['fecha'], reverse=True)[:10]
    
    def optimize_room_assignment(self, pacientes: List[Dict], salas: List[Dict]) -> Dict[str, List[str]]:
        """
        Optimiza la asignación de pacientes a salas usando algoritmo greedy.
        
        Args:
            pacientes: Lista de pacientes pendientes
            salas: Lista de salas disponibles
        
        Returns:
            Dict con asignaciones óptimas {sala_code: [patient_codes]}
        """
        # Algoritmo greedy simple
        # En producción: usar optimización más sofisticada (Hungarian algorithm, etc.)
        
        asignaciones = {sala['codigo']: [] for sala in salas}
        
        # Ordenar pacientes por prioridad (nivel de triaje)
        pacientes_ordenados = sorted(
            pacientes,
            key=lambda p: self._get_priority_score(p),
            reverse=True
        )
        
        # Asignar a sala con menor carga
        for paciente in pacientes_ordenados:
            # Encontrar sala con menos pacientes
            sala_optima = min(
                salas,
                key=lambda s: len(asignaciones[s['codigo']])
            )
            
            # Verificar capacidad
            if len(asignaciones[sala_optima['codigo']]) < sala_optima.get('plazas', 10):
                asignaciones[sala_optima['codigo']].append(paciente['patient_code'])
        
        return asignaciones
    
    def _get_load_level(self, pacientes: int) -> str:
        """Determina el nivel de carga."""
        if pacientes < 5:
            return 'baja'
        elif pacientes < 10:
            return 'media'
        else:
            return 'alta'
    
    def _get_priority_score(self, paciente: Dict) -> int:
        """Calcula puntuación de prioridad."""
        nivel_triaje = paciente.get('nivel_triaje', 'NIVEL V')
        
        scores = {
            'NIVEL I': 5,
            'NIVEL II': 4,
            'NIVEL III': 3,
            'NIVEL IV': 2,
            'NIVEL V': 1
        }
        
        return scores.get(nivel_triaje, 0)
    
    def _recommend_shifts(self, demandas_dia: List[float]) -> List[Dict]:
        """Recomienda turnos basados en demanda del día."""
        turnos = []
        
        # Turno mañana (8-15)
        demanda_manana = np.mean(demandas_dia[8:15])
        if demanda_manana > 10:
            turnos.append({
                'turno': 'Mañana',
                'horario': '08:00-15:00',
                'personal_recomendado': max(2, round(demanda_manana / 5)),
                'prioridad': 'alta' if demanda_manana > 15 else 'media'
            })
        
        # Turno tarde (15-22)
        demanda_tarde = np.mean(demandas_dia[15:22])
        if demanda_tarde > 10:
            turnos.append({
                'turno': 'Tarde',
                'horario': '15:00-22:00',
                'personal_recomendado': max(2, round(demanda_tarde / 5)),
                'prioridad': 'alta' if demanda_tarde > 15 else 'media'
            })
        
        # Turno noche (22-8)
        demanda_noche = np.mean([*demandas_dia[22:], *demandas_dia[:8]])
        if demanda_noche > 5:
            turnos.append({
                'turno': 'Noche',
                'horario': '22:00-08:00',
                'personal_recomendado': max(1, round(demanda_noche / 5)),
                'prioridad': 'media' if demanda_noche > 10 else 'baja'
            })
        
        return turnos
    
    def _generate_staffing_justification(self, demandas_dia: List[float]) -> str:
        """Genera justificación para recomendación de staffing."""
        demanda_max = max(demandas_dia)
        hora_pico = demandas_dia.index(demanda_max)
        
        return f"""
        Basado en el análisis predictivo:
        - Pico de demanda esperado a las {hora_pico}:00 con {round(demanda_max)} pacientes
        - Demanda promedio del día: {round(np.mean(demandas_dia))} pacientes
        - Se recomienda reforzar el personal durante las horas pico
        """


# Instancia global del servicio
_ml_service = MLPredictiveService()

def get_ml_service() -> MLPredictiveService:
    """Obtiene la instancia del servicio ML."""
    return _ml_service
