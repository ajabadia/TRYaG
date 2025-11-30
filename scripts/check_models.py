# check_models.py (versión de prueba final)
import google.generativeai as genai

# --- IMPORTANTE ---
# Pega tu clave de API MÁS RECIENTE aquí, directamente entre las comillas.
# Asegúrate de que no haya espacios antes o después.
API_KEY = "AIzaSyC8sV0M56YzCDL-O5n6m5emMLmtHjdxN3s" 

try:
    genai.configure(api_key=API_KEY)
    with open("temp_models_list.txt", "w", encoding="utf-8") as f:
        f.write("✅ ¡Conexión exitosa! Listando modelos...\n")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"   -> Modelo compatible encontrado: {m.name}\n")
                print(f"   -> Modelo compatible encontrado: {m.name}")

except Exception as e:
    print(f"❌ Error al ejecutar la prueba: {e}")


