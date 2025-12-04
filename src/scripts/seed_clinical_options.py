"""
Script para poblar la base de datos con opciones clínicas estándar.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.connection import get_database as get_db
from src.db.models import ClinicalOption

def seed_clinical_options():
    print("🌱 Seeding Clinical Options...")
    db = get_db()
    collection = db["clinical_options"]
    
    # Limpiar colección existente (opcional, para desarrollo)
    collection.delete_many({})
    
    options = [
        # --- ALERGIAS (Agentes Comunes) ---
        {"category": "allergy_agent", "value": "penicilina", "label": "Penicilina y derivados", "risk_level": "high"},
        {"category": "allergy_agent", "value": "sulfamidas", "label": "Sulfamidas"},
        {"category": "allergy_agent", "value": "cefalosporinas", "label": "Cefalosporinas"},
        {"category": "allergy_agent", "value": "quinolonas", "label": "Quinolonas"},
        {"category": "allergy_agent", "value": "aines", "label": "AINEs (Aspirina, Ibuprofeno...)"},
        {"category": "allergy_agent", "value": "opioides", "label": "Opioides"},
        {"category": "allergy_agent", "value": "latex", "label": "Látex", "risk_level": "high"},
        {"category": "allergy_agent", "value": "contrastes", "label": "Medios de Contraste Yodados"},
        {"category": "allergy_agent", "value": "clorhexidina", "label": "Clorhexidina"},
        {"category": "allergy_agent", "value": "huevos", "label": "Huevos"},
        {"category": "allergy_agent", "value": "frutos_secos", "label": "Frutos Secos / Cacahuetes", "risk_level": "high"},
        
        # --- PATOLOGÍAS CRÓNICAS ---
        {"category": "pathology", "value": "hta", "label": "Hipertensión Arterial (HTA)"},
        {"category": "pathology", "value": "diabetes_1", "label": "Diabetes Tipo 1"},
        {"category": "pathology", "value": "diabetes_2", "label": "Diabetes Tipo 2"},
        {"category": "pathology", "value": "epoc", "label": "EPOC / Bronquitis Crónica"},
        {"category": "pathology", "value": "asma", "label": "Asma"},
        {"category": "pathology", "value": "insuf_cardiaca", "label": "Insuficiencia Cardíaca"},
        {"category": "pathology", "value": "fa", "label": "Fibrilación Auricular"},
        {"category": "pathology", "value": "iam_previo", "label": "Infarto previo (IAM)"},
        {"category": "pathology", "value": "irc", "label": "Insuficiencia Renal Crónica"},
        {"category": "pathology", "value": "dialisis", "label": "En Diálisis"},
        {"category": "pathology", "value": "cirrosis", "label": "Cirrosis / Hepatitis Crónica"},
        {"category": "pathology", "value": "ictus", "label": "Ictus / ACV previo"},
        {"category": "pathology", "value": "epilepsia", "label": "Epilepsia"},
        {"category": "pathology", "value": "demencia", "label": "Demencia / Alzheimer"},
        
        # --- HÁBITOS SOCIALES ---
        {"category": "social_habit", "value": "tabaco", "label": "Fumador Activo"},
        {"category": "social_habit", "value": "ex_tabaco", "label": "Ex-Fumador"},
        {"category": "social_habit", "value": "alcohol", "label": "Consumo de Alcohol (Riesgo)"},
        {"category": "social_habit", "value": "drogas", "label": "Consumo de Drogas"},
        
        # --- SITUACIÓN CONVIVENCIA ---
        {"category": "living_situation", "value": "solo", "label": "Vive solo"},
        {"category": "living_situation", "value": "acompanado", "label": "Vive acompañado (Familia/Pareja)"},
        {"category": "living_situation", "value": "institucionalizado", "label": "Institucionalizado (Residencia)"},
        {"category": "living_situation", "value": "sin_hogar", "label": "Sin hogar"},
        
        # --- ESTADO FUNCIONAL ---
        {"category": "functional_status", "value": "independiente", "label": "Independiente (ABVD)"},
        {"category": "functional_status", "value": "baston", "label": "Camina con ayuda (Bastón/Andador)"},
        {"category": "functional_status", "value": "silla", "label": "Silla de Ruedas"},
        {"category": "functional_status", "value": "encamado", "label": "Encamado / Dependiente Total"},
    ]
    
    for opt_data in options:
        opt = ClinicalOption(**opt_data)
        # Usar update_one con upsert para evitar duplicados si se corre varias veces sin borrar
        collection.update_one(
            {"category": opt.category, "value": opt.value},
            {"$set": opt.model_dump(by_alias=True, exclude={"id"})},
            upsert=True
        )
        
    print(f"✅ Inserted/Updated {len(options)} clinical options.")

if __name__ == "__main__":
    seed_clinical_options()
