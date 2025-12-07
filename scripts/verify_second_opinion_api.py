import requests
import json
import sys

# Define base URL (assuming localhost mapping to 8000)
BASE_URL = "http://localhost:8000/v1/ai/reasoning"

def verify_api():
    print("🚀 Verifying /v1/ai/reasoning API Endpoint...")
    
    payload = {
        "patient_id": "test_patient",
        "query": "Paciente con fiebre alta y exantema. ¿Posible dengue?",
        "include_rag": True
    }
    
    try:
        # Note: This requires the API service to be up and running.
        # Since we are running outside the container network, we hit localhost:8000
        response = requests.post(BASE_URL, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response Success!")
            print(f"Model Used: {data.get('model_used')}")
            print(f"RAG Used: {data.get('rag_used')}")
            print("Analysis Snippet:", str(data.get('analysis'))[:100] + "...")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"⚠️ Connection Error (Is Docker API running?): {e}")

if __name__ == "__main__":
    verify_api()
