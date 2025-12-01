
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.db.connection import get_database
from src.db.models import ClinicalOption

def seed_clinical_options():
    try:
        db = get_database()
        collection = db['clinical_options']
        
        # Clear existing GI options to avoid duplicates/conflicts during dev
        collection.delete_many({"category": {"$regex": "^gi_"}})
        
        options = [
            # --- MAIN CATEGORIES ---
            {"category": "gi_category", "value": "trauma", "label": "🤕 Traumatismo / Golpe / Caída", "meta": {"order": 1}},
            {"category": "gi_category", "value": "pain", "label": "⚡ Dolor (Sin golpe previo)", "meta": {"order": 2}},
            {"category": "gi_category", "value": "infection", "label": "🌡️ Fiebre / Infección / Malestar", "meta": {"order": 3}},
            {"category": "gi_category", "value": "respiratory", "label": "🫁 Respiratorio (Tos, Ahogo)", "meta": {"order": 4}},
            {"category": "gi_category", "value": "other", "label": "❓ Otro", "meta": {"order": 5}},

            # --- TRAUMA MECHANISMS ---
            {"category": "gi_trauma_mechanism", "value": "Caída", "label": "Caída", "meta": {"order": 1}},
            {"category": "gi_trauma_mechanism", "value": "Golpe directo", "label": "Golpe directo", "meta": {"order": 2}},
            {"category": "gi_trauma_mechanism", "value": "Corte/Herida", "label": "Corte/Herida", "meta": {"order": 3}},
            {"category": "gi_trauma_mechanism", "value": "Accidente Tráfico", "label": "Accidente Tráfico", "meta": {"order": 4}},
            {"category": "gi_trauma_mechanism", "value": "Deportivo", "label": "Deportivo", "meta": {"order": 5}},

            # --- TRAUMA LOCATIONS ---
            {"category": "gi_trauma_location", "value": "Cabeza/Cara", "label": "Cabeza/Cara", "meta": {"order": 1}},
            {"category": "gi_trauma_location", "value": "Cuello", "label": "Cuello", "meta": {"order": 2}},
            {"category": "gi_trauma_location", "value": "Hombro/Brazo", "label": "Hombro/Brazo", "meta": {"order": 3}},
            {"category": "gi_trauma_location", "value": "Mano/Muñeca", "label": "Mano/Muñeca", "meta": {"order": 4}},
            {"category": "gi_trauma_location", "value": "Tórax/Espalda", "label": "Tórax/Espalda", "meta": {"order": 5}},
            {"category": "gi_trauma_location", "value": "Cadera/Pierna", "label": "Cadera/Pierna", "meta": {"order": 6}},
            {"category": "gi_trauma_location", "value": "Rodilla", "label": "Rodilla", "meta": {"order": 7}},
            {"category": "gi_trauma_location", "value": "Tobillo/Pie", "label": "Tobillo/Pie", "meta": {"order": 8}},

            # --- PAIN TYPES ---
            {"category": "gi_pain_type", "value": "Opresivo (peso)", "label": "Opresivo (peso)", "meta": {"order": 1}},
            {"category": "gi_pain_type", "value": "Punzante (pinchazo)", "label": "Punzante (pinchazo)", "meta": {"order": 2}},
            {"category": "gi_pain_type", "value": "Quemante (ardor)", "label": "Quemante (ardor)", "meta": {"order": 3}},
            {"category": "gi_pain_type", "value": "Cólico (va y viene)", "label": "Cólico (va y viene)", "meta": {"order": 4}},
            {"category": "gi_pain_type", "value": "Sordo (constante)", "label": "Sordo (constante)", "meta": {"order": 5}},

            # --- INFECTION SYMPTOMS ---
            {"category": "gi_infection_symptoms", "value": "Tos", "label": "Tos", "meta": {"order": 1}},
            {"category": "gi_infection_symptoms", "value": "Mocos", "label": "Mocos", "meta": {"order": 2}},
            {"category": "gi_infection_symptoms", "value": "Dolor de garganta", "label": "Dolor de garganta", "meta": {"order": 3}},
            {"category": "gi_infection_symptoms", "value": "Vómitos", "label": "Vómitos", "meta": {"order": 4}},
            {"category": "gi_infection_symptoms", "value": "Diarrea", "label": "Diarrea", "meta": {"order": 5}},
            {"category": "gi_infection_symptoms", "value": "Dolor al orinar", "label": "Dolor al orinar", "meta": {"order": 6}},
        ]

        for opt_data in options:
            opt = ClinicalOption(**opt_data)
            collection.insert_one(opt.model_dump(by_alias=True, exclude={"id"}))
        
        print(f"✅ Seeded {len(options)} clinical options for Guided Interview.")
    except Exception as e:
        print(f"❌ Error seeding options: {e}")

if __name__ == "__main__":
    seed_clinical_options()
