
"""
UI Rules Engine (Magic Cases)
Responsable de evaluar el estado del paciente y sugerir adaptaciones de interfaz
o alertas clínicas (Liquid UI).

Rules:
- Sepsis
- Ictus (Stroke)
- SCA (Cardio)
- Respiratory
- Pediatric/Geriatric
"""
import re

class UIRulesEngine:
    
    @staticmethod
    def evaluate(patient_data: dict) -> dict:
        """
        Analiza los datos del paciente y devuelve un dict con:
        - alerts: Lista de alertas (strings o dicts con severidad)
        - highlights: Lista de campos a resaltar (ej: 'sato2', 'ta')
        - suggestions: Acciones sugeridas (ej: 'ecg', 'cincinnati')
        """
        results = {
            "alerts": [],
            "highlights": [],
            "suggestions": []
        }
        
        # Datos base
        motivo = (patient_data.get('texto_medico') or "").lower()
        edad = patient_data.get('edad')
        vitals = patient_data.get('vital_signs', {})
        
        # --- 1. MAGIC CASE: PROBABLE SEPSIS ---
        # Regla: Fiebre (>38) + (Tachycardia (>100) OR Hypotension (<90 sys))
        temp = float(vitals.get('temperature') or 0)
        hr = float(vitals.get('heart_rate') or 0)
        sys_bp = float(vitals.get('systolic_bp') or 120)
        
        if temp > 38.0 and (hr > 100 or sys_bp < 90):
            results['alerts'].append({
                "type": "critical",
                "message": "🚨 ALERTA SEPSIS: Fiebre + Inestabilidad Hemodinámica detectada."
            })
            results['highlights'].extend(['temperature', 'heart_rate', 'systolic_bp'])
            results['suggestions'].append("qSOFA")

        # --- 2. MAGIC CASE: CÓDIGO ICTUS (STROKE) ---
        # Keywords: habla, boca, fuerza, brazo, hormigueo, comisura
        stroke_keywords = ['habla', 'boca', 'fuerza', 'brazo', 'hormigueo', 'comisura', 'paralisis', 'sonreir']
        if any(w in motivo for w in stroke_keywords):
             results['alerts'].append({
                "type": "warning",
                "message": "🧠 POSIBLE ICTUS: Palabras clave neurológicas detectadas."
            })
             results['suggestions'].append("Escala Cincinnati")

        # --- 3. MAGIC CASE: SÍNDROME CORONARIO (SCA) ---
        # Keywords: pecho, opresion, toracico, mandibula, brazo izquierdo
        sca_keywords = ['pecho', 'opresion', 'toracico', 'mandibula', 'corazon']
        if any(w in motivo for w in sca_keywords):
             results['highlights'].extend(['systolic_bp', 'heart_rate'])
             results['suggestions'].append("Electrocardiograma (ECG)")
             if "dolor" not in motivo:
                 results['suggestions'].append("Evaluar EVA Dolor")

        # --- 4. MAGIC CASE: RESPIRATORIO ---
        # Keywords: disnea, ahogo, aire, respirar
        resp_keywords = ['disnea', 'ahogo', 'aire', 'respirar', 'fatiga']
        if any(w in motivo for w in resp_keywords):
            results['highlights'].append('oxygen_saturation')
            # Check SpO2 if available
            spo2 = float(vitals.get('oxygen_saturation') or 100)
            if spo2 < 92:
                 results['alerts'].append({
                    "type": "critical",
                    "message": "🫁 HIPOXIA DETECTADA: Saturación < 92%."
                })

        # --- 5. MAGIC CASE: PEDIÁTRICO ---
        if edad is not None and isinstance(edad, int) and edad < 14:
            results['alerts'].append({
                "type": "info",
                "message": "👶 PACIENTE PEDIÁTRICO: Rangos de signos vitales ajustados."
            })
            # En el futuro esto podría cambiar la escala de colores de los inputs

        # --- 6. MAGIC CASE: GERIÁTRICO (RIESGO CAÍDAS) ---
        if edad is not None and isinstance(edad, int) and edad > 75:
            results['suggestions'].append("Test de Riesgo de Caídas")
            if "confus" in motivo or "desorient" in motivo:
                 results['alerts'].append({
                    "type": "warning",
                    "message": "👴 POSIBLE DELIRIUM: Valorar estado cognitivo agudo."
                })

        # --- 7. MAGIC CASE: TRAUMA / DOLOR ---
        trauma_keywords = ['caida', 'golpe', 'accidente', 'dolor', 'herida']
        if any(w in motivo for w in trauma_keywords):
             results['highlights'].append('pain_level')

        return results
