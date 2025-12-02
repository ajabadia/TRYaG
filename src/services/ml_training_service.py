import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os
from datetime import datetime
from db.connection import get_database

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'models')

class MLTrainingService:
    def __init__(self):
        self.db = get_database()
        if not os.path.exists(MODELS_DIR):
            os.makedirs(MODELS_DIR)
            
    def fetch_training_data(self):
        """Obtiene datos de entrenamiento de MongoDB."""
        # Obtener todos los registros completados (sintéticos y reales)
        # Se busca tanto 'timestamp' como 'arrival_time' para compatibilidad
        cursor = self.db.triage_records.find(
            {"status": "completed"},
            {
                "timestamp": 1, 
                "arrival_time": 1, 
                "triage_level": 1, 
                "triage_result.final_priority": 1,
                "wait_time_minutes": 1, 
                "_id": 0
            }
        )
        data = list(cursor)
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Normalizar columnas
            # 1. Fecha: Usar timestamp si existe, sino arrival_time
            if 'timestamp' in df.columns:
                df['arrival_time'] = df['timestamp'].fillna(df.get('arrival_time'))
            
            # 2. Nivel: Usar triage_result.final_priority si existe, sino triage_level
            if 'triage_result' in df.columns:
                # Extraer final_priority de triage_result (puede ser dict o NaN)
                def extract_priority(x):
                    if isinstance(x, dict):
                        return x.get('final_priority')
                    return x
                
                df['real_priority'] = df['triage_result'].apply(extract_priority)
                df['triage_level'] = df['real_priority'].fillna(df.get('triage_level'))
                
        return df
        
    def train_demand_model(self, df):
        """Entrena modelo de predicción de demanda."""
        print("Entrenando modelo de demanda...")
        
        # Feature Engineering: Agrupar por hora y día
        df['hour'] = pd.to_datetime(df['arrival_time']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['arrival_time']).dt.dayofweek
        df['date'] = pd.to_datetime(df['arrival_time']).dt.date
        
        # Contar pacientes por hora
        demand_df = df.groupby(['date', 'hour', 'day_of_week']).size().reset_index(name='patient_count')
        
        X = demand_df[['hour', 'day_of_week']]
        y = demand_df['patient_count']
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Guardar modelo
        joblib.dump(model, os.path.join(MODELS_DIR, 'demand_model.joblib'))
        print("Modelo de demanda guardado.")
        return model
        
    def train_wait_time_model(self, df):
        """Entrena modelo de predicción de tiempo de espera."""
        print("Entrenando modelo de tiempo de espera...")
        
        # Feature Engineering
        df['hour'] = pd.to_datetime(df['arrival_time']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['arrival_time']).dt.dayofweek
        
        # Variables predictoras: Hora, Día, Nivel de Triaje
        X = df[['hour', 'day_of_week', 'triage_level']]
        y = df['wait_time_minutes']
        
        # Limpiar datos faltantes si los hay
        X = X.fillna(0)
        y = y.fillna(0)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Guardar modelo
        joblib.dump(model, os.path.join(MODELS_DIR, 'wait_time_model.joblib'))
        print("Modelo de tiempo de espera guardado.")
        return model

    def train_all(self):
        """Ejecuta el pipeline completo de entrenamiento."""
        df = self.fetch_training_data()
        
        if df.empty:
            return {"status": "error", "msg": "No hay datos suficientes para entrenar."}
            
        self.train_demand_model(df)
        self.train_wait_time_model(df)
        
        return {"status": "success", "msg": f"Modelos entrenados con {len(df)} registros."}

if __name__ == "__main__":
    service = MLTrainingService()
    result = service.train_all()
    print(result)
