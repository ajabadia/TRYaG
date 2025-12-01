
import os
import sys
from datetime import datetime

# Add project root to path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.db.connection import get_database
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
        {"category": "immuno_onco", "value": "pid", "label": "Inmunodeficiencia Primaria", "meta": {"is_immuno": True, "is_onco": False}},
        {"category": "immuno_onco", "value": "autoimmune_sys", "label": "Enfermedad Autoinmune Sistémica (Lupus, AR)", "meta": {"is_immuno": True, "is_onco": False}},
        {"category": "immuno_onco", "value": "cancer_metastatic", "label": "Cáncer Metastásico", "meta": {"is_immuno": False, "is_onco": True}},
        {"category": "immuno_onco", "value": "cancer_hematologic", "label": "Neoplasia Hematológica (Leucemia, Linfoma)", "meta": {"is_immuno": True, "is_onco": True}},
        {"category": "immuno_onco", "value": "cancer_solid", "label": "Tumor Sólido Activo", "meta": {"is_immuno": False, "is_onco": True}},
        {"category": "immuno_onco", "value": "cancer_history", "label": "Antecedentes de Cáncer (Remisión)", "meta": {"is_immuno": False, "is_onco": True}},

        # --- ALLERGIES (Agents - Merged Food & Drugs) ---
        # Drugs
        {"category": "allergy_agent", "value": "penicillin", "label": "Penicilina / Betalactámicos", "meta": {"type": "drug"}},
        {"category": "allergy_agent", "value": "nsaids", "label": "AINEs (Ibuprofeno, Aspirina)", "meta": {"type": "drug"}},
        {"category": "allergy_agent", "value": "sulfonamides", "label": "Sulfamidas", "meta": {"type": "drug"}},
        {"category": "allergy_agent", "value": "opioids", "label": "Opioides", "meta": {"type": "drug"}},
        {"category": "allergy_agent", "value": "contrast_iodine", "label": "Contraste Yodado", "meta": {"type": "drug"}},
        {"category": "allergy_agent", "value": "anesthetics_local", "label": "Anestésicos Locales", "meta": {"type": "drug"}},
        {"category": "allergy_agent", "value": "latex", "label": "Látex", "meta": {"type": "environmental"}},
        # Food
        {"category": "allergy_agent", "value": "gluten", "label": "Gluten (Celiaquía)", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "lactose", "label": "Lactosa", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "nuts", "label": "Frutos Secos", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "shellfish", "label": "Marisco / Crustáceos", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "egg", "label": "Huevo", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "milk_protein", "label": "Proteína Leche Vaca (APLV)", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "fish", "label": "Pescado", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "soy", "label": "Soja", "meta": {"type": "food"}},
        {"category": "allergy_agent", "value": "fruits_rosaceae", "label": "Frutas Rosáceas (Melocotón, etc.)", "meta": {"type": "food"}},

        # --- ALLERGIES (Reactions) ---
        {"category": "allergy_reaction", "value": "anaphylaxis", "label": "Anafilaxia (Shock)", "risk_level": "high"},
        {"category": "allergy_reaction", "value": "angioedema", "label": "Angioedema (Hinchazón cara/glotis)", "risk_level": "high"},
        {"category": "allergy_reaction", "value": "bronchospasm", "label": "Broncoespasmo / Disnea Severa", "risk_level": "high"},
        {"category": "allergy_reaction", "value": "hypotension", "label": "Hipotensión / Colapso", "risk_level": "high"},
        {"category": "allergy_reaction", "value": "urticaria", "label": "Urticaria / Rash", "risk_level": "low"},
        {"category": "allergy_reaction", "value": "gi_symptoms", "label": "Síntomas Gastrointestinales", "risk_level": "low"},
        
        # --- VACCINES ---
        {"category": "vaccine", "value": "tetanus", "label": "Tétanos (Últimos 10 años)"},
        {"category": "vaccine", "value": "flu", "label": "Gripe (Campaña actual)"},
        {"category": "vaccine", "value": "covid19", "label": "COVID-19 (Pauta completa/Refuerzo)"},
        {"category": "vaccine", "value": "pneumococcus", "label": "Neumococo (Prevenar/Pneumovax)"},
        {"category": "vaccine", "value": "hepatitis_b", "label": "Hepatitis B"},
        {"category": "vaccine", "value": "hepatitis_a", "label": "Hepatitis A"},
        {"category": "vaccine", "value": "mmr", "label": "Triple Vírica (Sarampión, Rubeola, Paperas)"},
        {"category": "vaccine", "value": "hpv", "label": "VPH (Papiloma)"},
        {"category": "vaccine", "value": "meningococcus", "label": "Meningococo (ACWY/B)"},
        {"category": "vaccine", "value": "zoster", "label": "Herpes Zóster"},

        # --- IMPLANTS / DEVICES ---
        {"category": "implant", "value": "pacemaker", "label": "Marcapasos / DAI"},
        {"category": "implant", "value": "valve_mechanic", "label": "Válvula Cardíaca Mecánica"},
        {"category": "implant", "value": "valve_bio", "label": "Válvula Cardíaca Biológica"},
        {"category": "implant", "value": "stent_coronary", "label": "Stent Coronario"},
        {"category": "implant", "value": "stent_vascular", "label": "Stent Vascular Periférico/Aórtico"},
        {"category": "implant", "value": "joint_prosthesis_hip", "label": "Prótesis Total de Cadera"},
        {"category": "implant", "value": "joint_prosthesis_knee", "label": "Prótesis Total de Rodilla"},
        {"category": "implant", "value": "osteosynthesis", "label": "Material de Osteosíntesis (Placas/Clavos)"},
        {"category": "implant", "value": "cochlear", "label": "Implante Coclear"},
        {"category": "implant", "value": "vp_shunt", "label": "Válvula de Derivación Ventriculoperitoneal"},
        {"category": "implant", "value": "portacath", "label": "Port-a-Cath / Reservorio Venoso"},
        {"category": "implant", "value": "insulin_pump", "label": "Bomba de Insulina"},
        {"category": "implant", "value": "iud", "label": "DIU (Dispositivo Intrauterino)"},

        # --- DEMENTIA / COGNITIVE ---
        {"category": "dementia", "value": "alzheimer", "label": "Enfermedad de Alzheimer"},
        {"category": "dementia", "value": "vascular", "label": "Demencia Vascular"},
        {"category": "dementia", "value": "lewy_body", "label": "Demencia por Cuerpos de Lewy"},
        {"category": "dementia", "value": "frontotemporal", "label": "Demencia Frontotemporal"},
        {"category": "dementia", "value": "parkinson", "label": "Demencia asociada a Parkinson"},
        {"category": "dementia", "value": "mild_cognitive", "label": "Deterioro Cognitivo Leve"},
        {"category": "dementia", "value": "intellectual_disability", "label": "Discapacidad Intelectual"},
        {"category": "dementia", "value": "mixed", "label": "Demencia Mixta"},

        # --- MRSA / MULTIRESISTANT ---
        {"category": "mrsa_type", "value": "mrsa", "label": "S. Aureus Resistente a Meticilina (SARM)"},
        {"category": "mrsa_type", "value": "blee", "label": "E. Coli / Klebsiella BLEE"},
        {"category": "mrsa_type", "value": "kpc", "label": "Carbapenemasas (KPC/OXA/NDM)"},
        {"category": "mrsa_type", "value": "vre", "label": "Enterococo Resistente a Vancomicina"},
        {"category": "mrsa_type", "value": "pseudomonas_mdr", "label": "Pseudomonas Multirresistente"},
        {"category": "mrsa_type", "value": "acinetobacter", "label": "Acinetobacter Baumannii MDR"},
        {"category": "mrsa_type", "value": "candida_auris", "label": "Candida Auris"},
        {"category": "mrsa_type", "value": "c_diff", "label": "Clostridioides difficile"},

        # --- FAMILY HISTORY ---
        # Cardio
        {"category": "family_cardio", "value": "mi_early", "label": "Infarto Agudo Miocardio Precoz (<55H, <65M)"},
        {"category": "family_cardio", "value": "sudden_death", "label": "Muerte Súbita"},
        {"category": "family_cardio", "value": "stroke", "label": "Ictus / ACV Precoz"},
        {"category": "family_cardio", "value": "cardiomyopathy", "label": "Miocardiopatía Familiar"},
        {"category": "family_cardio", "value": "arrhythmia", "label": "Arritmias Hereditarias (Brugada, QT Largo)"},
        # Cancer
        {"category": "family_cancer", "value": "breast", "label": "Cáncer de Mama (BRCA)"},
        {"category": "family_cancer", "value": "colon", "label": "Cáncer de Colon (Lynch/Poliposis)"},
        {"category": "family_cancer", "value": "ovary", "label": "Cáncer de Ovario"},
        {"category": "family_cancer", "value": "prostate", "label": "Cáncer de Próstata"},
        {"category": "family_cancer", "value": "pancreas", "label": "Cáncer de Páncreas"},
        {"category": "family_cancer", "value": "melanoma", "label": "Melanoma Familiar"},
        # Diabetes/Endo
        {"category": "family_diabetes", "value": "t1dm", "label": "Diabetes Tipo 1"},
        {"category": "family_diabetes", "value": "t2dm", "label": "Diabetes Tipo 2"},
        {"category": "family_diabetes", "value": "thyroid", "label": "Enfermedad Tiroidea Autoinmune"},
        # Genetic
        {"category": "family_genetic", "value": "huntington", "label": "Enfermedad de Huntington"},
        {"category": "family_genetic", "value": "cf", "label": "Fibrosis Quística"},
        {"category": "family_genetic", "value": "hemochromatosis", "label": "Hemocromatosis"},
        {"category": "family_genetic", "value": "thrombophilia", "label": "Trombofilias Hereditarias (Factor V Leiden, etc.)"},
        {"category": "family_genetic", "value": "marfan", "label": "Síndrome de Marfan"},

        # --- ANIMAL CONTACT ---
        {"category": "animal_contact", "value": "dogs_cats", "label": "Perros / Gatos (Domésticos)"},
        {"category": "animal_contact", "value": "farm", "label": "Animales de Granja (Ganado, Cerdos, Aves)"},
        {"category": "animal_contact", "value": "birds", "label": "Aves (Psitacosis)"},
        {"category": "animal_contact", "value": "reptiles", "label": "Reptiles (Salmonella)"},
        {"category": "animal_contact", "value": "rodents", "label": "Roedores"},
        {"category": "animal_contact", "value": "wild", "label": "Animales Salvajes / Caza"},
        {"category": "animal_contact", "value": "exotic", "label": "Mascotas Exóticas"},
        {"category": "animal_contact", "value": "horses", "label": "Caballos"},

        # --- SENSORY ---
        # Auditory
        {"category": "sensory_auditory", "value": "deaf_total", "label": "Sordera Total (Cofosis)"},
        {"category": "sensory_auditory", "value": "hypoacusis", "label": "Hipoacusia (Requiere audífono)"},
        {"category": "sensory_auditory", "value": "tinnitus", "label": "Acúfenos / Tinnitus Severo"},
        # Visual
        {"category": "sensory_visual", "value": "blind_total", "label": "Ceguera Total"},
        {"category": "sensory_visual", "value": "low_vision", "label": "Baja Visión (No corregible con gafas)"},
        {"category": "sensory_visual", "value": "glaucoma", "label": "Glaucoma"},
        {"category": "sensory_visual", "value": "maculopathy", "label": "Maculopatía"},
        # Language (20+ common languages)
        {"category": "sensory_language", "value": "spanish", "label": "Español"},
        {"category": "sensory_language", "value": "english", "label": "Inglés"},
        {"category": "sensory_language", "value": "french", "label": "Francés"},
        {"category": "sensory_language", "value": "german", "label": "Alemán"},
        {"category": "sensory_language", "value": "italian", "label": "Italiano"},
        {"category": "sensory_language", "value": "portuguese", "label": "Portugués"},
        {"category": "sensory_language", "value": "chinese", "label": "Chino (Mandarín/Cantonés)"},
        {"category": "sensory_language", "value": "arabic", "label": "Árabe"},
        {"category": "sensory_language", "value": "russian", "label": "Ruso"},
        {"category": "sensory_language", "value": "ukrainian", "label": "Ucraniano"},
        {"category": "sensory_language", "value": "romanian", "label": "Rumano"},
        {"category": "sensory_language", "value": "polish", "label": "Polaco"},
        {"category": "sensory_language", "value": "bulgarian", "label": "Búlgaro"},
        {"category": "sensory_language", "value": "hindi", "label": "Hindi"},
        {"category": "sensory_language", "value": "urdu", "label": "Urdu"},
        {"category": "sensory_language", "value": "bengali", "label": "Bengalí"},
        {"category": "sensory_language", "value": "tagalog", "label": "Tagalo (Filipinas)"},
        {"category": "sensory_language", "value": "vietnamese", "label": "Vietnamita"},
        {"category": "sensory_language", "value": "japanese", "label": "Japonés"},
        {"category": "sensory_language", "value": "korean", "label": "Coreano"},
        {"category": "sensory_language", "value": "wolof", "label": "Wolof"},
        {"category": "sensory_language", "value": "bambara", "label": "Bambara"},
        {"category": "sensory_language", "value": "sign_language", "label": "Lengua de Signos"},
        # Prosthesis
        {"category": "sensory_prosthesis", "value": "dental_removable", "label": "Prótesis Dental Removible"},
        {"category": "sensory_prosthesis", "value": "limb_lower_bk", "label": "Prótesis M. Inferior (Transtibial)"},
        {"category": "sensory_prosthesis", "value": "limb_lower_ak", "label": "Prótesis M. Inferior (Transfemoral)"},
        {"category": "sensory_prosthesis", "value": "limb_upper", "label": "Prótesis Miembro Superior"},
        {"category": "sensory_prosthesis", "value": "ocular", "label": "Prótesis Ocular"},

        # --- FORENSIC ---
        # Violence
        {"category": "forensic_violence", "value": "physical", "label": "Violencia Física"},
        {"category": "forensic_violence", "value": "sexual", "label": "Violencia Sexual"},
        {"category": "forensic_violence", "value": "psychological", "label": "Violencia Psicológica"},
        {"category": "forensic_violence", "value": "gender_violence", "label": "Violencia de Género"},
        {"category": "forensic_violence", "value": "domestic", "label": "Violencia Doméstica"},
        {"category": "forensic_violence", "value": "elder_abuse", "label": "Maltrato a Ancianos"},
        {"category": "forensic_violence", "value": "child_abuse", "label": "Maltrato Infantil"},
        {"category": "forensic_violence", "value": "neglect", "label": "Negligencia / Abandono"},
        {"category": "forensic_violence", "value": "self_harm", "label": "Autolesiones"},
        # Cultural
        {"category": "forensic_cultural", "value": "language_barrier", "label": "Barrera Idiomática"},
        {"category": "forensic_cultural", "value": "gender_pref_pro", "label": "Preferencia Género Profesional"},
        {"category": "forensic_cultural", "value": "modesty", "label": "Pudor / Privacidad Estricta"},
        {"category": "forensic_cultural", "value": "family_decision", "label": "Toma de decisiones familiar"},
        # Religion
        {"category": "forensic_religion", "value": "jehovah_witness", "label": "Testigos de Jehová (Rechazo Transfusión)"},
        {"category": "forensic_religion", "value": "diet_halal", "label": "Dieta Halal"},
        {"category": "forensic_religion", "value": "diet_kosher", "label": "Dieta Kosher"},
        {"category": "forensic_religion", "value": "ramadan", "label": "Ayuno (Ramadán)"},
        {"category": "forensic_religion", "value": "rel_vegetarian", "label": "Dieta Vegetariana/Vegana (Preferencia)"},
        {"category": "forensic_religion", "value": "no_pork", "label": "No consume cerdo"},
        {"category": "forensic_religion", "value": "prayer_times", "label": "Horarios de Rezo"},

        # --- SOCIAL HABITS ---
        {"category": "social_habit", "value": "tobacco_active", "label": "Fumador Activo"},
        {"category": "social_habit", "value": "tobacco_ex", "label": "Ex-Fumador"},
        {"category": "social_habit", "value": "alcohol_social", "label": "Alcohol (Consumo Social)"},
        {"category": "social_habit", "value": "alcohol_risk", "label": "Alcohol (Consumo de Riesgo)"},
        {"category": "social_habit", "value": "alcohol_dependence", "label": "Alcohol (Dependencia/Alcoholismo)"},
        {"category": "social_habit", "value": "drugs_cannabis", "label": "Cannabis"},
        {"category": "social_habit", "value": "drugs_cocaine", "label": "Cocaína / Estimulantes"},
        {"category": "social_habit", "value": "drugs_opioids", "label": "Opioides (Heroína, Fentanilo)"},
        {"category": "social_habit", "value": "drugs_synthetic", "label": "Drogas de Diseño / Sintéticas"},
        {"category": "social_habit", "value": "gambling", "label": "Ludopatía"},

        # --- LIVING SITUATION ---
        {"category": "living_situation", "value": "alone", "label": "Vive Solo/a"},
        {"category": "living_situation", "value": "family", "label": "Con Familia (Cónyuge/Hijos)"},
        {"category": "living_situation", "value": "parents", "label": "Con Padres"},
        {"category": "living_situation", "value": "institution", "label": "Institucionalizado (Residencia)"},
        {"category": "living_situation", "value": "caregiver", "label": "Con Cuidador/a"},
        {"category": "living_situation", "value": "homeless", "label": "Sin Hogar"},
        {"category": "living_situation", "value": "shelter", "label": "Albergue / Centro de Acogida"},

        # --- FUNCTIONAL STATUS ---
        {"category": "functional_status", "value": "independent", "label": "Independiente (Barthel > 90)"},
        {"category": "functional_status", "value": "mild_dependence", "label": "Dependencia Leve (Barthel 60-90)"},
        {"category": "functional_status", "value": "moderate_dependence", "label": "Dependencia Moderada (Barthel 40-55)"},
        {"category": "functional_status", "value": "severe_dependence", "label": "Dependencia Severa (Barthel 20-35)"},
        {"category": "functional_status", "value": "total_dependence", "label": "Dependencia Total (Barthel < 20)"},

        # --- DIET TYPE ---
        {"category": "diet_type", "value": "normal", "label": "Dieta Normal / Basal"},
        {"category": "diet_type", "value": "diabetic", "label": "Dieta Diabética"},
        {"category": "diet_type", "value": "low_sodium", "label": "Dieta Hiposódica (Sin Sal)"},
        {"category": "diet_type", "value": "soft", "label": "Dieta Blanda / Protección Gástrica"},
        {"category": "diet_type", "value": "pureed", "label": "Dieta Triturada / Túrmix"},
        {"category": "diet_type", "value": "diet_vegetarian", "label": "Dieta Vegetariana"},
        {"category": "diet_type", "value": "diet_vegan", "label": "Dieta Vegana"},
        {"category": "diet_type", "value": "gluten_free", "label": "Dieta Sin Gluten"},
        {"category": "diet_type", "value": "renal", "label": "Dieta Renal (Baja en Potasio/Proteína)"},

        # --- PSYCH DIAGNOSIS ---
        {"category": "psych_diagnosis", "value": "depression", "label": "Trastorno Depresivo"},
        {"category": "psych_diagnosis", "value": "anxiety", "label": "Trastorno de Ansiedad"},
        {"category": "psych_diagnosis", "value": "bipolar", "label": "Trastorno Bipolar"},
        {"category": "psych_diagnosis", "value": "schizophrenia", "label": "Esquizofrenia / Trastorno Psicótico"},
        {"category": "psych_diagnosis", "value": "ptsd", "label": "Trastorno de Estrés Postraumático (TEPT)"},
        {"category": "psych_diagnosis", "value": "ocd", "label": "Trastorno Obsesivo-Compulsivo (TOC)"},
        {"category": "psych_diagnosis", "value": "personality", "label": "Trastorno de Personalidad (Límite, etc.)"},
        {"category": "psych_diagnosis", "value": "eating_disorder", "label": "Trastorno Conducta Alimentaria (Anorexia/Bulimia)"},
        {"category": "psych_diagnosis", "value": "substance_abuse", "label": "Trastorno por Uso de Sustancias"},

        # --- PSYCH MEDICATION ---
        {"category": "psych_medication", "value": "ssri", "label": "ISRS (Fluoxetina, Sertralina, Escitalopram)"},
        {"category": "psych_medication", "value": "snri", "label": "Duales (Venlafaxina, Duloxetina)"},
        {"category": "psych_medication", "value": "tricyclic", "label": "Tricíclicos (Amitriptilina)"},
        {"category": "psych_medication", "value": "benzodiazepine", "label": "Benzodiacepinas (Diazepam, Lorazepam)"},
        {"category": "psych_medication", "value": "antipsychotic_atypical", "label": "Antipsicóticos Atípicos (Quetiapina, Olanzapina)"},
        {"category": "psych_medication", "value": "antipsychotic_typical", "label": "Antipsicóticos Típicos (Haloperidol)"},
        {"category": "psych_medication", "value": "mood_stabilizer", "label": "Estabilizadores (Litio, Valproico)"},
        {"category": "psych_medication", "value": "stimulant", "label": "Estimulantes (Metilfenidato)"},

        # --- OCCUPATIONAL RISK ---
        {"category": "occupational_risk", "value": "healthcare", "label": "Personal Sanitario (Biológico/Radiación)"},
        {"category": "occupational_risk", "value": "chemical", "label": "Industria Química / Limpieza (Tóxicos)"},
        {"category": "occupational_risk", "value": "construction", "label": "Construcción (Polvo/Asbesto/Trauma)"},
        {"category": "occupational_risk", "value": "agriculture", "label": "Agricultura/Ganadería (Pesticidas/Zoonosis)"},
        {"category": "occupational_risk", "value": "mining", "label": "Minería (Silicosis)"},
        {"category": "occupational_risk", "value": "laboratory", "label": "Laboratorio (Biológico/Químico)"},
        {"category": "occupational_risk", "value": "food_processing", "label": "Procesado de Alimentos (Alérgenos/Frío)"},
        {"category": "occupational_risk", "value": "education", "label": "Educación (Infeccioso/Voz)"},
        {"category": "occupational_risk", "value": "office", "label": "Oficina (Ergonómico/Sedentarismo)"},

        # --- PAIN LOCATION ---
        {"category": "pain_location", "value": "headache", "label": "Cefalea / Migraña"},
        {"category": "pain_location", "value": "cervical", "label": "Cervicalgia"},
        {"category": "pain_location", "value": "lumbar", "label": "Lumbalgia / Ciática"},
        {"category": "pain_location", "value": "joint_knee", "label": "Artrosis/Artritis Rodilla"},
        {"category": "pain_location", "value": "joint_hip", "label": "Artrosis/Artritis Cadera"},
        {"category": "pain_location", "value": "joint_shoulder", "label": "Hombro Doloroso"},
        {"category": "pain_location", "value": "neuropathic", "label": "Dolor Neuropático (Polineuropatía)"},
        {"category": "pain_location", "value": "fibromyalgia", "label": "Fibromialgia / Dolor Generalizado"},
        {"category": "pain_location", "value": "abdominal_chronic", "label": "Dolor Abdominal Crónico"},
        {"category": "pain_location", "value": "pelvic", "label": "Dolor Pélvico Crónico"},

        # --- PAIN CHARACTERISTICS (HDA) ---
        {"category": "pain_characteristics", "value": "sharp", "label": "Punzante / Agudo"},
        {"category": "pain_characteristics", "value": "dull", "label": "Sordo / Pesado"},
        {"category": "pain_characteristics", "value": "oppressive", "label": "Opresivo (Como un peso)"},
        {"category": "pain_characteristics", "value": "burning", "label": "Quemante / Urente"},
        {"category": "pain_characteristics", "value": "colicky", "label": "Cólico (Va y viene)"},
        {"category": "pain_characteristics", "value": "throbbing", "label": "Pulsátil (Latidos)"},
        {"category": "pain_characteristics", "value": "electric", "label": "Eléctrico / Calambre"},
        {"category": "pain_characteristics", "value": "stabbing", "label": "Taladrante"},

        # --- ALLERGY SYMPTOMS ---
        {"category": "allergy_symptoms", "value": "rash", "label": "Erupción Cutánea / Exantema"},
        {"category": "allergy_symptoms", "value": "urticaria", "label": "Urticaria (Ronchas)"},
        {"category": "allergy_symptoms", "value": "pruritus", "label": "Prurito (Picor)"},
        {"category": "allergy_symptoms", "value": "angioedema", "label": "Angioedema (Hinchazón labios/ojos)"},
        {"category": "allergy_symptoms", "value": "dyspnea", "label": "Disnea (Dificultad respiratoria)"},
        {"category": "allergy_symptoms", "value": "wheezing", "label": "Sibilancias (Pitos)"},
        {"category": "allergy_symptoms", "value": "nausea", "label": "Náuseas / Vómitos"},
        {"category": "allergy_symptoms", "value": "diarrhea", "label": "Diarrea"},
        {"category": "allergy_symptoms", "value": "hypotension", "label": "Mareo / Hipotensión"},
        {"category": "allergy_symptoms", "value": "anaphylaxis", "label": "Shock Anafiláctico"},
    ]

    print(f"Seeding {len(options_data)} clinical options...")
    
    count_upserted = 0
    
    for data in options_data:
        try:
            collection.update_one(
                {"category": data["category"], "value": data["value"]},
                {"$set": {
                    "label": data["label"],
                    "meta": data.get("meta"),
                    "risk_level": data.get("risk_level"),
                    "active": True
                }},
                upsert=True
            )
            count_upserted += 1
        except Exception as e:
            print(f"Error upserting {data['category']}/{data['value']}: {e}")
            
    print(f"Seeding complete. Processed: {count_upserted}")

if __name__ == "__main__":
    seed_clinical_options()
