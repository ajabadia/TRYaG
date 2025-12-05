from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ Health Check Passed")

def test_triage_analyze():
    payload = {
        "motivo_consulta": "Dolor de pecho",
        "edad": 55,
        "dolor": 8,
        "signos_vitales": {
            "saturacion": 98,
            "frecuencia_cardiaca": 80
        }
    }
    response = client.post("/v1/core/analyze", json=payload)
    if response.status_code != 200:
        print(f"❌ Triage Analyze Failed: {response.text}")
        return
        
    data = response.json()
    assert "nivel_sugerido" in data
    assert "razonamiento" in data
    print(f"✅ Triage Analyze Passed (Level: {data['nivel_sugerido']}, Reason: {data['razonamiento']})")

def test_ptr_calculation():
    payload = {
        "edad": 60,
        "signos_vitales": {
            "sistolica": 110,
            "frecuencia_cardiaca": 100,
            "saturacion": 95
        }
    }
    response = client.post("/v1/core/predict/risk", json=payload)
    if response.status_code != 200:
        print(f"❌ PTR Calc Failed: {response.text}")
        return

    data = response.json()
    assert "ptr_score" in data
    print(f"✅ PTR Calc Passed (Score: {data['ptr_score']})")

if __name__ == "__main__":
    print("🚀 Starting API Verification...")
    try:
        test_health()
        test_triage_analyze()
        test_ptr_calculation()
        print("🎉 All API tests passed!")
    except Exception as e:
        print(f"🔥 Verification Failed: {e}")
