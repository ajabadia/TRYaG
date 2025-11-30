import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Fallback to secrets.toml logic or hardcoded for test
    try:
        import toml
        secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            api_key = secrets.get("GOOGLE_API_KEY")
    except:
        pass

if not api_key:
    print("API Key not found")
    sys.exit(1)

genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"
PROMPT = """## ROL ##
Eres un sistema experto de alerta temprana clínica. Analizas signos vitales y antecedentes para detectar riesgos inminentes ANTES de la valoración médica completa.

## TAREA ##
Analiza los datos proporcionados y genera alertas si detectas valores fuera de rango o combinaciones peligrosas (ej: Sepsis, Shock, Crisis Hipertensiva).

## INPUTS ##
- Edad: 40
- Signos Vitales: FC: 80.0, SPO2: 98.0, EVA: 7.0, TEMP: 38.0, PAS: 120.0, PAD: 80.0, FR: 16.0, GCS: 15.0, PUPILAS: Normal, OXIGENO_SUPLEMENTARIO: False
- Antecedentes: Hábitos: Fumador Activo
Social: Vive acompañado (Familia/Pareja)
- Alergias: No conocidas

## REGLAS ##
1. Sé extremadamente sensible a signos de inestabilidad hemodinámica o respiratoria.
2. Si todo es normal, devuelve una lista vacía de alertas y riesgo "Low".
3. Formato JSON EXACTO:
{
  "risk_level": "High" | "Medium" | "Low",
  "alerts": ["Alerta 1", "Alerta 2"]
}
"""

def debug_request():
    with open("debug_output_utf8.txt", "w", encoding="utf-8") as f:
        f.write(f"Testing model: {MODEL_NAME}\n")
        f.write("Sending prompt...\n")
        
        generation_config = {
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
        
        model = genai.GenerativeModel(model_name=MODEL_NAME, generation_config=generation_config)
        
        try:
            response = model.generate_content(PROMPT)
            
            f.write("\n--- Response Object ---\n")
            f.write(f"Parts: {len(response.parts)}\n")
            
            if response.prompt_feedback:
                f.write(f"Prompt Feedback: {response.prompt_feedback}\n")
                
            if response.candidates:
                 f.write(f"Finish Reason: {response.candidates[0].finish_reason}\n")
                 f.write(f"Safety Ratings: {response.candidates[0].safety_ratings}\n")
            
            if response.text:
                f.write(f"\nText: {response.text}\n")
                
        except Exception as e:
            f.write(f"Exception: {e}\n")

if __name__ == "__main__":
    debug_request()
