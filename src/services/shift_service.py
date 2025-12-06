from datetime import datetime, timedelta
from typing import Dict, Any, List
import streamlit as st
from db.repositories.triage import get_triage_repository
from services.gemini_client import GeminiService
from services.contingency_service import is_contingency_active
from core.prompt_manager import PromptManager

class ShiftService:
    def __init__(self):
        self.triage_repo = get_triage_repository()
        self.gemini_service = GeminiService()
        self.prompt_manager = PromptManager()
        self._ensure_prompt_exists()

    def _ensure_prompt_exists(self):
        """Asegura que el prompt 'shift_handoff' exista en el repositorio."""
        try:
            prompt_type = "shift_handoff"
            if not self.prompt_manager.get_prompt(prompt_type):
                base_prompt = """
        Actúa como un Supervisor de Enfermería de Urgencias. Genera un "Informe de Relevo de Turno" (Shift Handoff) profesional y conciso en Markdown.

        **Datos del Turno (Últimas {hours} horas):**
        - Total Pacientes Vistos: {total_patients}
        - Desglose por Niveles: {level_counts}
        - Desglose por Especialidad: {specialty_counts}
        
        **Casos Destacados/Críticos:**
        {critical_summary}

        **Instrucciones:**
        1. Empieza con un resumen ejecutivo ("Turno tranquilo", "Alta carga", etc. inferido de los datos).
        2. Presenta las estadísticas principales en formato lista o tabla.
        3. Resume los casos críticos si los hay.
        4. No inventes pacientes, usa solo los datos proporcionados.
        5. Usa tono clínico formal en Español.
                """
                # Crear versión inicial
                self.prompt_manager.create_version(
                    prompt_type=prompt_type,
                    content=base_prompt,
                    model="gemini-2.5-flash",
                    author="system",
                    notes="Prompt inicial para relevo de turno"
                )
                # Activarla (asumiendo v1, pero set_active maneja IDs)
                versions = self.prompt_manager.list_versions(prompt_type)
                if versions:
                    # Sort or find the one we just created?
                    # Normally create_version returns ID.
                    # Re-fetching to be safe or optimize prompt_manager usage in future.
                    # For now just picking first available if any.
                    vid = list(versions.keys())[0] 
                    self.prompt_manager.set_active_version(prompt_type, vid)
        except Exception as e:
            print(f"Error ensuring shift prompt: {e}")

    def _generate_fallback_report(self, hours, total, level_counts, specialty_counts, critical_cases):
        """Genera un informe básico determinista sin usar IA."""
        lines = []
        lines.append(f"# 📋 Informe de Relevo (Generado Automáticamente)")
        lines.append(f"**Periodo:** Últimas {hours} horas")
        lines.append(f"**Generado:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lines.append("")
        lines.append("## Resumen Estadístico")
        lines.append(f"- **Total Pacientes:** {total}")
        lines.append("- **Por Niveles:**")
        for k, v in level_counts.items():
            lines.append(f"  - Nivel {k}: {v}")
        lines.append("- **Por Especialidad:**")
        for k, v in specialty_counts.items():
            lines.append(f"  - {k}: {v}")
        lines.append("")
        
        if critical_cases:
            lines.append("## ⚠️ Casos Críticos/Destacados")
            for c in critical_cases:
                lines.append(f"- **{c['motivo']}** (Nivel {c['nivel']})")
                lines.append(f"  - Paciente: {c['sexo']} {c['edad']} años")
        else:
            lines.append("## Casos Destacados")
            lines.append("No se registraron casos críticos en este periodo.")
            
        lines.append("")
        lines.append("---")
        lines.append("*Este informe fue generado sin IA debido a una interrupción del servicio.*")
        return "\n".join(lines)

    def generate_handoff_report(self, hours: int = 8, start_date: datetime = None, end_date: datetime = None) -> str:
        """
        Genera un informe de relevo basado en los triajes de las últimas X horas o rango personalizado.
        """
        # 1. Contingency Check
        if is_contingency_active():
            # Intentar generar reporte básico en contingencia
            period_str = f"Últimas {hours} horas" if not start_date else f"{start_date.strftime('%H:%M')} - {end_date.strftime('%H:%M')}"
            return self._generate_fallback_report(period_str, 0, {}, {}, []) 

        # Configurar fechas
        if start_date and end_date:
            pass # Usar las pasadas
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours)

        # Formato para el prompt
        period_str = f"Desde {start_date.strftime('%d/%m %H:%M')} hasta {end_date.strftime('%d/%m %H:%M')}"
        if not (start_date and end_date): # Si fue calculado por horas
             period_str += f" (Últimas {hours} horas)"

        # 2. Obtener registros
        records = self.triage_repo.get_by_date_range(start_date, end_date)

        if not records:
            return f"## Informe de Relevo\n\nNo se han registrado pacientes en el periodo: {period_str}."

        # 3. Pre-procesar estadísticas
        total_patients = len(records)
        level_counts = {}
        specialty_counts = {}
        critical_cases = []

        for r in records:
            level = str(r.get('final_priority', 'Indeterminado'))
            level_counts[level] = level_counts.get(level, 0) + 1
            
            spec = r.get('ia_result', {}).get('specialty', 'General')
            specialty_counts[spec] = specialty_counts.get(spec, 0) + 1

            is_critical = False
            if 'I' in level or '1' in level or 'Rojo' in level or 'Naranja' in level:
                if 'III' not in level and 'IV' not in level:
                    is_critical = True
            
            if is_critical:
                critical_cases.append({
                    "sexo": r.get('patient_snapshot', {}).get('sex', '?'),
                    "edad": r.get('patient_snapshot', {}).get('age', '?'),
                    "motivo": r.get('ia_result', {}).get('reason', 'Sin motivo'),
                    "nivel": level
                })

        # 4. Obtener Prompt desde PromptManager
        prompt_data = self.prompt_manager.get_prompt("shift_handoff")
        
        # Si no hay prompt configurado o falla algo, usar fallback
        if not prompt_data:
             return self._generate_fallback_report(period_str, total_patients, level_counts, specialty_counts, critical_cases)
            
        base_prompt = prompt_data.get("content", "")
        # Usar el modelo configurado o el nuevo deseado por defecto
        model_name = prompt_data.get("model") or "gemini-2.5-flash"

        version_id = prompt_data.get("version_id", "unknown")

        critical_summary = ""
        for c in critical_cases[:10]:
            critical_summary += f"- Paciente {c['sexo']} {c['edad']}a: {c['motivo']} ({c['nivel']})\n"

        fill_params = {
            "{hours}": period_str, # Reemplazamos {hours} por el string descriptivo del periodo
            "{total_patients}": str(total_patients),
            "{level_counts}": str(level_counts),
            "{specialty_counts}": str(specialty_counts),
            "{critical_summary}": critical_summary
        }
        
        final_prompt = base_prompt
        for k, v in fill_params.items():
            final_prompt = final_prompt.replace(k, v)

        # 5. Llamar a Gemini
        try:
            generation_config = {
                "temperature": 0.7,
            }
            
            response_data, _ = self.gemini_service.generate_content(
                caller_id="shift_service",
                user_id="system", 
                call_type="shift_report",
                prompt_type="shift_handoff",
                prompt_version_id=version_id,
                model_name=model_name,
                prompt_content=final_prompt,
                generation_config=generation_config
            )
            
            if response_data.get("status") == "ERROR":
                # Si falla la IA, devolvemos el reporte básico
                st.toast("Fallo en IA, generando reporte básico...", icon="⚠️")
                return self._generate_fallback_report(hours, total_patients, level_counts, specialty_counts, critical_cases)
                
            return response_data.get("text", "No se generó texto.")

        except Exception as e:
            # Fallback en caso de Excepción
            st.toast(f"Error IA ({str(e)}), generando reporte básico.", icon="⚠️")
            return self._generate_fallback_report(hours, total_patients, level_counts, specialty_counts, critical_cases)

        except Exception as e:
            return f"Error inesperado generando informe: {e}"

# Singleton
_shift_service = None
def get_shift_service():
    global _shift_service
    if _shift_service is None:
        _shift_service = ShiftService()
    return _shift_service
