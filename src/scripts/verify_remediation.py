# path: src/scripts/verify_remediation.py
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.repositories.salas import get_sala, update_sala_plazas
from db.repositories.notification_config import save_vapid_config, get_vapid_config

def test_room_updates():
    print("\n--- Testing Room Capacity Atomic Updates ---")
    
    # 1. Pick a room code (mock or real if exists, we'll try 'ADM-01' or create dummy)
    room_code = "TEST_ROOM_999"
    
    # Ensure room exists for test
    from db.connection import get_database
    db = get_database()
    db.salas.update_one(
        {"codigo": room_code},
        {"$set": {"codigo": room_code, "plazas_disponibles": 10, "tipo": "test"}},
        upsert=True
    )
    
    initial = get_sala(room_code)
    print(f"Initial: {initial.get('plazas_disponibles')}")
    
    # 2. Occupy a seat (-1)
    print("Occupying seat (-1)...")
    update_sala_plazas(room_code, -1)
    
    after_occupy = get_sala(room_code)
    print(f"After Occupy: {after_occupy.get('plazas_disponibles')}")
    
    if after_occupy.get('plazas_disponibles') == 9:
        print("✅ Success: Plazas decreased by 1")
    else:
        print(f"❌ Failure: Expected 9, got {after_occupy.get('plazas_disponibles')}")

    # 3. Release a seat (+1)
    print("Releasing seat (+1)...")
    update_sala_plazas(room_code, 1)
    
    final = get_sala(room_code)
    print(f"Final: {final.get('plazas_disponibles')}")
    
    if final.get('plazas_disponibles') == 10:
        print("✅ Success: Plazas restored")
    else:
         print(f"❌ Failure: Expected 10, got {final.get('plazas_disponibles')}")

    # Cleanup
    db.salas.delete_one({"codigo": room_code})

def test_vapid_config():
    print("\n--- Testing VAPID Config Persistence ---")
    
    dummy_config = {
        "private_key": "test_priv_key",
        "public_key": "test_pub_key",
        "subject": "mailto:test@test.com"
    }
    
    print("Saving dummy VAPID config...")
    save_vapid_config(dummy_config)
    
    print("Retrieving VAPID config...")
    retrieved = get_vapid_config()
    
    if retrieved.get("private_key") == "test_priv_key":
         print("✅ Success: Config persisted and retrieved")
    else:
         print(f"❌ Failure: {retrieved}")

if __name__ == "__main__":
    try:
        test_room_updates()
        test_vapid_config()
        print("\n🎉 Verification Completed")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
