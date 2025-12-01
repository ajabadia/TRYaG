
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.db.database import get_database
from src.db.models import ClinicalOption

def seed_clinical_options():
    db = get_database()
    collection = db["clinical_options"]
    
    # Clear existing options (optional, but good for development)
    # collection.delete_many({}) 
    # For now, let's use upsert logic based on category + value to avoid duplicates but keep existing

    options_data = [
        # --- IMMUNO / ONCO ---
        {"category": "immuno_onco", "value": "hiv", "label": "VIH / SIDA", "meta": {"is_immuno": True, "is_onco": False}},
        {"category": "immuno_onco", "value": "transplant_organ", "label": "Trasplante de Órgano Sólido", "meta": {"is_immuno": True, "is_onco": False}},
        {"category": "immuno_onco", "value": "transplant_marrow", "label": "Trasplante de Médula Ósea", "meta": {"is_immuno": True, "is_onco": True}},
        {"category": "immuno_onco", "value": "chemo_active", "label": "Quimioterapia Activa (<3 meses)", "meta": {"is_immuno": True, "is_onco": True}},
        {"category": "immuno_onco", "value": "radio_active", "label": "Radioterapia Activa", "meta": {"is_immuno": True, "is_onco": True}},
        {"category": "immuno_onco", "value": "immunotherapy", "label": "Inmunoterapia / Biológicos", "meta": {"is_immuno": True, "is_onco": True}},
        {"category": "immuno_onco", "value": "corticoids_chronic", "label": "Corticoides Sistémicos Crónicos", "meta": {"is_immuno": True, "is_onco": False}},
        {"category": "immuno_onco", "value": "asplenia", "label": "Asplenia (Sin bazo)", "meta": {"is_immuno": True, "is_onco": False}},
        {"category": "immuno_onco", "value": "neutropenia", "label": "Neutropenia Crónica", "meta": {"is_immuno": True, "is_onco": False}},
        {"category": "immuno_onco", "value": "cancer_metastatic", "label": "Cáncer Metastásico", "meta": {"is_immuno": False, "is_onco": True}},
        {"category": "immuno_onco", "value": "cancer_hematologic", "label": "Neoplasia Hematológica (Leucemia, Linfoma)", "meta": {"is_immuno": True, "is_onco": True}},
        {"category": "immuno_onco", "value": "cancer_solid", "label": "Tumor Sólido Activo", "meta": {"is_immuno": False, "is_onco": True}},

        # --- ALLERGIES (High Risk) ---
        {"category": "allergy_reaction", "value": "anaphylaxis", "label": "Anafilaxia (Shock)", "risk_level": "high"},
        {"category": "allergy_reaction", "value": "angioedema", "label": "Angioedema (Hinchazón cara/glotis)", "risk_level": "high"},
        {"category": "allergy_reaction", "value": "bronchospasm", "label": "Broncoespasmo / Disnea Severa", "risk_level": "high"},
        {"category": "allergy_reaction", "value": "hypotension", "label": "Hipotensión / Colapso", "risk_level": "high"},
        
        # --- VACCINES ---
        {"category": "vaccine", "value": "tetanus", "label": "Tétanos (Últimos 10 años)"},
        {"category": "vaccine", "value": "flu", "label": "Gripe (Campaña actual)"},
        {"category": "vaccine", "value": "covid19", "label": "COVID-19 (Pauta completa/Refuerzo)"},
        {"category": "vaccine", "value": "pneumococcus", "label": "Neumococo"},
        {"category": "vaccine", "value": "hepatitis_b", "label": "Hepatitis B"},

        # --- IMPLANTS / DEVICES ---
        {"category": "implant", "value": "pacemaker", "label": "Marcapasos / DAI"},
        {"category": "implant", "value": "valve_mechanic", "label": "Válvula Cardíaca Mecánica"},
        {"category": "implant", "value": "valve_bio", "label": "Válvula Cardíaca Biológica"},
        {"category": "implant", "value": "stent_coronary", "label": "Stent Coronario"},
        {"category": "implant", "value": "joint_prosthesis", "label": "Prótesis Articular (Cadera/Rodilla)"},
        {"category": "implant", "value": "cochlear", "label": "Implante Coclear"},
        {"category": "implant", "value": "vp_shunt", "label": "Válvula de Derivación Ventriculoperitoneal"},
        {"category": "implant", "value": "portacath", "label": "Port-a-Cath / Reservorio Venoso"},
        {"category": "implant", "value": "insulin_pump", "label": "Bomba de Insulina"},

        # --- DEMENTIA / COGNITIVE ---
        {"category": "dementia", "value": "alzheimer", "label": "Enfermedad de Alzheimer"},
        {"category": "dementia", "value": "vascular", "label": "Demencia Vascular"},
        {"category": "dementia", "value": "lewy_body", "label": "Demencia por Cuerpos de Lewy"},
        {"category": "dementia", "value": "frontotemporal", "label": "Demencia Frontotemporal"},
        {"category": "dementia", "value": "parkinson", "label": "Demencia asociada a Parkinson"},
        {"category": "dementia", "value": "mild_cognitive", "label": "Deterioro Cognitivo Leve"},
        {"category": "dementia", "value": "intellectual_disability", "label": "Discapacidad Intelectual"},

        # --- MRSA / MULTIRESISTANT ---
        {"category": "mrsa_type", "value": "mrsa", "label": "S. Aureus Resistente a Meticilina (SARM)"},
        {"category": "mrsa_type", "value": "blee", "label": "E. Coli / Klebsiella BLEE"},
        {"category": "mrsa_type", "value": "kpc", "label": "Carbapenemasas (KPC/OXA)"},
        {"category": "mrsa_type", "value": "vre", "label": "Enterococo Resistente a Vancomicina"},
        {"category": "mrsa_type", "value": "pseudomonas_mdr", "label": "Pseudomonas Multirresistente"},
        {"category": "mrsa_type", "value": "candida_auris", "label": "Candida Auris"},

        # --- FAMILY HISTORY ---
        {"category": "family_cardio", "value": "mi_early", "label": "Infarto Agudo Miocardio Precoz (<55 hombres, <65 mujeres)"},
        {"category": "family_cardio", "value": "sudden_death", "label": "Muerte Súbita"},
        {"category": "family_cardio", "value": "stroke", "label": "Ictus / ACV"},
        
        {"category": "family_cancer", "value": "breast", "label": "Cáncer de Mama (BRCA)"},
        {"category": "family_cancer", "value": "colon", "label": "Cáncer de Colon (Lynch)"},
        {"category": "family_cancer", "value": "ovary", "label": "Cáncer de Ovario"},
        {"category": "family_cancer", "value": "prostate", "label": "Cáncer de Próstata"},

        {"category": "family_diabetes", "value": "t1dm", "label": "Diabetes Tipo 1"},
        {"category": "family_diabetes", "value": "t2dm", "label": "Diabetes Tipo 2"},

        {"category": "family_genetic", "value": "huntington", "label": "Enfermedad de Huntington"},
        {"category": "family_genetic", "value": "cf", "label": "Fibrosis Quística"},
        {"category": "family_genetic", "value": "hemochromatosis", "label": "Hemocromatosis"},
        {"category": "family_genetic", "value": "thrombophilia", "label": "Trombofilias Hereditarias"},

        # --- FOOD ALLERGIES ---
        {"category": "food_allergy", "value": "gluten", "label": "Gluten (Celiaquía)"},
        {"category": "food_allergy", "value": "lactose", "label": "Lactosa"},
        {"category": "food_allergy", "value": "nuts", "label": "Frutos Secos"},
        {"category": "food_allergy", "value": "shellfish", "label": "Marisco / Crustáceos"},
        {"category": "food_allergy", "value": "egg", "label": "Huevo"},
        {"category": "food_allergy", "value": "milk_protein", "label": "Proteína Leche Vaca (APLV)"},
        {"category": "food_allergy", "value": "fish", "label": "Pescado"},
        {"category": "food_allergy", "value": "soy", "label": "Soja"},

        # --- ANIMAL CONTACT ---
        {"category": "animal_contact", "value": "farm", "label": "Animales de Granja (Ganado, Cerdos, Aves)"},
        {"category": "animal_contact", "value": "birds", "label": "Aves (Psitacosis)"},
        {"category": "animal_contact", "value": "reptiles", "label": "Reptiles (Salmonella)"},
        {"category": "animal_contact", "value": "rodents", "label": "Roedores"},
        {"category": "animal_contact", "value": "wild", "label": "Animales Salvajes / Caza"},
        {"category": "animal_contact", "value": "exotic", "label": "Mascotas Exóticas"},

        # --- SENSORY ---
        {"category": "sensory_auditory", "value": "deaf_total", "label": "Sordera Total (Cofosis)"},
        {"category": "sensory_auditory", "value": "hypoacusis", "label": "Hipoacusia (Requiere audífono)"},
        
        {"category": "sensory_visual", "value": "blind_total", "label": "Ceguera Total"},
        {"category": "sensory_visual", "value": "low_vision", "label": "Baja Visión (No corregible con gafas)"},
        
        {"category": "sensory_language", "value": "sign_language", "label": "Lengua de Signos"},
        {"category": "sensory_language", "value": "foreign_only", "label": "Solo Idioma Extranjero (Requiere Intérprete)"},
        
        {"category": "sensory_prosthesis", "value": "dental", "label": "Prótesis Dental Removible"},
        {"category": "sensory_prosthesis", "value": "limb_lower", "label": "Prótesis Miembro Inferior"},
        {"category": "sensory_prosthesis", "value": "limb_upper", "label": "Prótesis Miembro Superior"},

        # --- FORENSIC ---
        {"category": "forensic_violence", "value": "physical", "label": "Violencia Física"},
        {"category": "forensic_violence", "value": "sexual", "label": "Violencia Sexual"},
        {"category": "forensic_violence", "value": "psychological", "label": "Violencia Psicológica"},
        {"category": "forensic_violence", "value": "neglect", "label": "Negligencia / Abandono"},
        
        {"category": "forensic_cultural", "value": "language_barrier", "label": "Barrera Idiomática"},
        {"category": "forensic_cultural", "value": "gender_pref", "label": "Preferencia Género Profesional"},
        
        {"category": "forensic_religion", "value": "jehovah_witness", "label": "Testigos de Jehová (Rechazo Transfusión)"},
        {"category": "forensic_religion", "value": "diet_halal", "label": "Dieta Halal"},
        {"category": "forensic_religion", "value": "diet_kosher", "label": "Dieta Kosher"},
        {"category": "forensic_religion", "value": "ramadan", "label": "Ayuno (Ramadán)"},
    ]

    print(f"Seeding {len(options_data)} clinical options...")
    
    count_new = 0
    count_updated = 0
    
    for data in options_data:
        # Check if exists
        existing = collection.find_one({"category": data["category"], "value": data["value"]})
        
        if existing:
            # Update if changed (simplification: just update fields)
            collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "label": data["label"],
                    "meta": data.get("meta"),
                    "risk_level": data.get("risk_level"),
                    "active": True
                }}
            )
            count_updated += 1
        else:
            # Insert new
            new_option = ClinicalOption(**data)
            collection.insert_one(new_option.model_dump(by_alias=True))
            count_new += 1
            
    print(f"Seeding complete. New: {count_new}, Updated: {count_updated}")

if __name__ == "__main__":
    seed_clinical_options()
