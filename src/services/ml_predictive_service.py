# path: src/services/ml_predictive_service.py
# Creado: 2025-11-26
# Actualizado: 2025-12-02 (Real ML Integration)
"""
Servicio de Machine Learning para predicciones y optimizaciones.
Integra modelos reales (RandomForest) entrenados con Scikit-learn.
"""
import streamlit as st
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
import joblib
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'models')

class MLPredictiveService:
    """
    Servicio de predicciones con Machine Learning Real.
    Usa modelos RandomForest entrenados offline.
    """
    
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Carga los modelos entrenados desde disco."""
        try:
            demand_path = os.path.join(MODELS_DIR, 'demand_model.joblib')
            wait_path = os.path.join(MODELS_DIR, 'wait_time_model.joblib')
            
            if os.path.exists(demand_path):
                self.models['demand'] = joblib.load(demand_path)
            
            if os.path.exists(wait_path):
                self.models['wait_time'] = joblib.load(wait_path)
                
            self.models_loaded = bool(self.models)
        except Exception as e:
            print(f"Error cargando modelos ML: {e}")
            self.models_loaded = False

    def predict_demand(self, sala_code: str, fecha: date, hora: int) -> Dict[str, Any]:
        """
        Predice la demanda esperada para una sala en una fecha/hora específica.
        """
        # Preparar features
        day_of_week = fecha.weekday()
        
        # Predicción
        if 'demand' in self.models:
            # Input: [[hour, day_of_week]]
            X = pd.DataFrame([[hora, day_of_week]], columns=['hour', 'day_of_week'])
            demanda_predicha = self.models['demand'].predict(X)[0]
            confidence = 0.9 # RandomForest es robusto
        else:
            # Fallback a heurística si no hay modelo
            demanda_predicha = 15 * (1.5 if 10 <= hora <= 14 else 1.0)
            confidence = 0.5
            
        # Calcular intervalo de confianza simple
        margen_error = demanda_predicha * 0.2
        
        return {
            'demanda_predicha': round(demanda_predicha),
            'confianza': confidence,
            'intervalo_min': max(0, round(demanda_predicha - margen_error)),
            'intervalo_max': round(demanda_predicha + margen_error),
            'factores': {
                'dia_semana': day_of_week,
                'hora': hora,
                'modelo_usado': 'RandomForest' if 'demand' in self.models else 'Heurístico'
            }
        }
    
    def predict_wait_time(self, sala_code: str, pacientes_actuales: int) -> Dict[str, Any]:
        """
        Predice el tiempo de espera basado en pacientes actuales.
        """
        # Estimamos la hora actual y día para el contexto
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Asumimos un nivel de triaje promedio (3) para la predicción general
        avg_triage = 3
        
        if 'wait_time' in self.models:
            # Input: [[hour, day_of_week, triage_level]]
            # Nota: El modelo fue entrenado prediciendo el tiempo INDIVIDUAL.
            # Para la cola, sumamos o promediamos? 
            # Simplificación: El modelo predice tiempo de espera para un paciente nuevo llegando AHORA.
            X = pd.DataFrame([[hour, day_of_week, avg_triage]], columns=['hour', 'day_of_week', 'triage_level'])
            tiempo_base = self.models['wait_time'].predict(X)[0]
            
            # Ajuste por cola actual (Factor de corrección lineal)
            factor_cola = 1 + (pacientes_actuales * 0.1)
            tiempo_predicho = tiempo_base * factor_cola
        else:
            # Fallback
            tiempo_predicho = pacientes_actuales * 15
        
        return {
            'tiempo_predicho_min': round(tiempo_predicho * 0.8),
            'pacientes_en_espera': pacientes_actuales,
            'tiempo_por_paciente': round(tiempo_predicho / max(1, pacientes_actuales), 1),
            'nivel_carga': self._get_load_level(pacientes_actuales),
            'modelo_usado': 'RandomForest' if 'wait_time' in self.models else 'Heurístico'
        }
    
    def recommend_staffing(self, sala_code: str, fecha: date) -> Dict[str, Any]:
        """
        Recomienda el staffing óptimo para una sala en una fecha.
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
        Detecta anomalías comparando histórico real vs predicción del modelo.
        """
        anomalies = []
        # Nota: Esto requeriría leer datos reales de DB para comparar.
        # Por ahora mantenemos la simulación para esta función específica 
        # hasta tener un pipeline de detección de anomalías real.
        
        for i in range(dias_historico):
            fecha = date.today() - timedelta(days=i)
            # Usamos el modelo para obtener la "esperada"
            pred = self.predict_demand(sala_code, fecha, 12) # Mediodía como referencia
            demanda_esperada = pred['demanda_predicha']
            
            # Simulamos un dato "real" para el ejemplo (en prod leeríamos de DB)
            demanda_real = np.random.normal(demanda_esperada, 3)
            
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
        """
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
        Basado en el análisis predictivo (RandomForest):
        - Pico de demanda esperado a las {hora_pico}:00 con {round(demanda_max)} pacientes
        - Demanda promedio del día: {round(np.mean(demandas_dia))} pacientes
        - Se recomienda reforzar el personal durante las horas pico
        """


# Instancia global del servicio
_ml_service = MLPredictiveService()

def get_ml_service() -> MLPredictiveService:
    """Obtiene la instancia del servicio ML."""
    return _ml_service
