import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try streamlit secrets style if env var generic fails (just in case, but standard is env)
    try:
        import streamlit as st
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

if not api_key:
    print("No API KEY found")
    exit(1)

genai.configure(api_key=api_key)

models_file = "available_models.txt"
print(f"Listing models to {models_file}...")
try:
    with open(models_file, "w", encoding="utf-8") as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                line = f"- {m.name}\n"
                print(line.strip())
                f.write(line)
except Exception as e:
    print(f"Error: {e}")
