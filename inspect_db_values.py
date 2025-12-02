
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from db import get_database
from ui.config.config_loader import load_centro_config

def inspect_values():
    with open('db_values.txt', 'w', encoding='utf-8') as f:
        try:
            db = get_database()
            config = load_centro_config()
            
            f.write("=== CONFIGURATION VALUES ===\n")
            
            # Roles
            f.write("\n[Roles]\n")
            try:
                roles = db["users"].distinct("role")
                f.write(f"Roles found: {roles}\n")
            except Exception as e:
                f.write(f"Error getting roles: {e}\n")

            # Rooms
            f.write("\n[Rooms Configuration]\n")
            salas = config.get('salas', [])
            types = set()
            subtypes = set()
            for s in salas:
                types.add(s.get('tipo'))
                subtypes.add(s.get('subtipo'))
            
            f.write(f"Room Types: {list(types)}\n")
            f.write(f"Room Subtypes: {list(subtypes)}\n")
            
            # Patient Flow States
            f.write("\n[Patient Flow States]\n")
            try:
                states = db["patient_flow"].distinct("estado")
                f.write(f"States found: {states}\n")
            except Exception as e:
                f.write(f"Error getting states: {e}\n")
            
            # Triage Levels
            f.write("\n[Triage Levels]\n")
            try:
                levels = db["triage_records"].distinct("triage_result.level")
                f.write(f"Triage Levels found: {levels}\n")
            except Exception as e:
                f.write(f"Error getting levels: {e}\n")

            # Specialties
            f.write("\n[Specialties]\n")
            try:
                specs = db["triage_records"].distinct("triage_result.specialty")
                f.write(f"Specialties found: {specs}\n")
            except Exception as e:
                f.write(f"Error getting specialties: {e}\n")

        except Exception as e:
            f.write(f"Critical error: {e}\n")

if __name__ == "__main__":
    inspect_values()
