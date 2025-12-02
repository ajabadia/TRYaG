from typing import List

class RecommendationService:
    """
    Service to generate self-care recommendations based on triage level and symptoms.
    """

    @staticmethod
    def get_recommendations(triage_level: int, main_symptom: str = None, pain_level: int = 0, interview_data: dict = None) -> List[str]:
        recommendations = []

        # 1. Recomendaciones por Nivel de Triaje
        if triage_level == 1: # Rojo
            recommendations.append("🚨 **ATENCIÓN INMEDIATA**: No ingerir alimentos ni líquidos.")
            recommendations.append("Mantener al paciente en reposo absoluto y monitorizado.")
        elif triage_level == 2: # Naranja
            recommendations.append("⚠️ **Emergencia**: Reposo absoluto. Avisar inmediatamente si hay cambios en el estado de conciencia.")
            recommendations.append("No ingerir alimentos hasta valoración médica.")
        elif triage_level == 3: # Amarillo
            recommendations.append("Reposo relativo en sala de espera.")
            recommendations.append("Avisar a enfermería si el dolor aumenta o aparecen nuevos síntomas.")
        elif triage_level >= 4: # Verde/Azul
            recommendations.append("Puede esperar sentado en la sala de espera.")
            recommendations.append("Mantenga la calma, será atendido en breve.")

        # 2. Recomendaciones por Síntomas (Keywords básicas o datos de entrevista)
        # Usamos datos de la entrevista si están disponibles, sino keywords del motivo
        
        symptom_text = (main_symptom or "").lower()
        
        # Trauma
        if "trauma" in symptom_text or "golpe" in symptom_text or "caída" in symptom_text or (interview_data and 'trauma' in interview_data):
            recommendations.append("🧊 **Traumatismo**: Aplicar frío local (hielo envuelto en paño) durante 15 min para reducir inflamación.")
            recommendations.append("Mantener la zona afectada elevada si es posible.")
            recommendations.append("No masajear la zona golpeada.")

        # Heridas / Sangrado
        if "sangre" in symptom_text or "herida" in symptom_text or "corte" in symptom_text or (interview_data and interview_data.get('trauma', {}).get('bleeding') != 'No'):
            recommendations.append("🩸 **Herida**: Mantener la zona limpia y cubierta.")
            recommendations.append("Si sangra, aplicar presión directa constante con una gasa limpia.")

        # Fiebre / Infección
        if "fiebre" in symptom_text or (interview_data and interview_data.get('infection', {}).get('fever') != 'No'):
            if triage_level >= 3: # Si no es crítico
                recommendations.append("🌡️ **Fiebre**: Mantenerse hidratado (pequeños sorbos de agua).")
                recommendations.append("Descubrirse ligeramente para facilitar la pérdida de calor.")

        # Dolor Alto
        if pain_level >= 7:
            recommendations.append("💊 **Dolor Intenso**: Si la espera se prolonga más de 30 min, solicitar re-evaluación para analgesia.")

        # Respiratorio
        if "respirar" in symptom_text or "aire" in symptom_text or (interview_data and 'respiratory' in interview_data):
             recommendations.append("🫁 **Respiratorio**: Mantenerse en posición sentada o semi-incorporada (Fowler).")
             recommendations.append("Intentar respiraciones lentas y profundas.")

        return recommendations
