import random
from datetime import datetime, timedelta
import pymongo
import sys
import os

# Añadir src al path para poder importar db.connection
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from db.connection import get_database

def generate_synthetic_data(num_records=1000):
    """
    Genera datos sintéticos de triaje para entrenamiento de ML.
    Marca los registros con 'is_synthetic': True.
    """
    try:
        db = get_database()
        collection = db['triage_records']
        
        # Limpiar datos sintéticos anteriores
        deleted = collection.delete_many({'is_synthetic': True})
        print(f"Eliminados {deleted.deleted_count} registros sintéticos anteriores.")
        
        records = []
        start_date = datetime.now() - timedelta(days=180)
        
        print(f"Generando {num_records} registros sintéticos...")
        
        for _ in range(num_records):
            # 1. Simular Fecha y Hora (Patrones realistas)
            days_offset = random.randint(0, 180)
            current_date = start_date + timedelta(days=days_offset)
            
            # Peso por día de la semana (Lunes=0, Domingo=6)
            weekday = current_date.weekday()
            if weekday == 0 or weekday == 4: # Lunes y Viernes más carga
                hour_weights = [1, 1, 1, 1, 1, 2, 4, 8, 10, 9, 8, 7, 6, 5, 4, 5, 7, 8, 6, 4, 3, 2, 1, 1]
            elif weekday >= 5: # Fin de semana menos carga pero urgencias constantes
                hour_weights = [2, 2, 2, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 6, 6, 6, 6, 7, 6, 5, 4, 3, 2]
            else: # Martes-Jueves estándar
                hour_weights = [1, 1, 1, 1, 1, 2, 3, 7, 9, 8, 7, 6, 5, 4, 4, 5, 6, 7, 5, 3, 2, 2, 1, 1]
                
            hour = random.choices(range(24), weights=hour_weights)[0]
            minute = random.randint(0, 59)
            arrival_time = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 2. Simular Nivel de Triaje (Peso realista)
            # Nivel 1 (Resucitación) muy raro, Nivel 4/5 (Leves) comunes
            triage_level = random.choices([1, 2, 3, 4, 5], weights=[1, 5, 20, 40, 34])[0]
            
            # 3. Simular Tiempo de Espera (Correlacionado con Nivel y "Carga")
            # Base wait time
            base_wait = {1: 0, 2: 5, 3: 30, 4: 60, 5: 120}[triage_level]
            
            # Factor aleatorio y de hora punta
            is_peak = 9 <= hour <= 13 or 17 <= hour <= 20
            peak_factor = 1.5 if is_peak else 0.8
            
            actual_wait_time = int(base_wait * peak_factor * random.uniform(0.8, 1.2))
            
            # 4. Construir registro (Schema Realista)
            audit_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
            audit_id = f"SYNTH-{arrival_time.strftime('%Y%m%d%H%M%S')}-{audit_suffix}"
            
            record = {
                "audit_id": audit_id, # Required unique index
                "patient_id": f"SYNTH_{random.randint(10000, 99999)}",
                "timestamp": arrival_time, # Real data uses timestamp
                "arrival_time": arrival_time, # Keep for compatibility if needed
                "patient_data": {
                    "edad": random.randint(18, 90),
                    "texto_medico": "Sintoma simulado para entrenamiento ML",
                    "vital_signs": {
                        "fc": random.randint(60, 100),
                        "pas": random.randint(100, 140),
                        "pad": random.randint(60, 90),
                        "spo2": random.randint(95, 100),
                        "fr": random.randint(12, 20),
                        "temp": round(random.uniform(36.0, 37.5), 1),
                        "gcs": 15
                    }
                },
                "triage_result": {
                    "final_priority": triage_level,
                    "status": "SUCCESS"
                },
                "triage_level": triage_level, # Flattened for easier access if needed
                "wait_time_minutes": actual_wait_time,
                "is_synthetic": True,
                "status": "completed"
            }
            records.append(record)
            
        if records:
            try:
                # Intentar insertar uno primero para verificar
                print("Intentando insertar 1 registro de prueba...")
                collection.insert_one(records[0])
                print("¡Éxito en prueba unitaria!")
                
                # Insertar el resto
                remaining = records[1:]
                if remaining:
                    print(f"Insertando {len(remaining)} registros restantes...")
                    collection.insert_many(remaining, ordered=False)
                    print(f"¡Éxito! Insertados {len(records)} registros sintéticos en 'triage_records'.")
            except pymongo.errors.BulkWriteError as bwe:
                print(f"Error de escritura en lote: {bwe.details}")
            except pymongo.errors.WriteError as we:
                print(f"Error de escritura: {we}")
            except Exception as e:
                print(f"Error general: {e}")
        else:
            print("No se generaron registros.")
            
    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    generate_synthetic_data()
