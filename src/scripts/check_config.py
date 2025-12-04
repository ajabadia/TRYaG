import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from db.repositories.centros import get_centros_repository

def check_config():
    print("🔍 Checking MongoDB Configuration...")
    try:
        repo = get_centros_repository()
        centro = repo.get_centro_principal()
        
        if not centro:
            print("❌ No main center configuration found!")
            return

        logo_path = centro.get("logo_path", "")
        print(f"ℹ️ Current logo_path: '{logo_path}'")
        
        if not logo_path:
            print("⚠️ logo_path is empty.")
        elif os.path.exists(logo_path):
            print("✅ logo_path points to an existing file.")
        elif os.path.exists(os.path.abspath(logo_path)):
             print(f"✅ logo_path (absolute) points to an existing file: {os.path.abspath(logo_path)}")
        else:
            print("❌ logo_path file NOT found on disk!")
            
    except Exception as e:
        print(f"❌ Error checking config: {e}")

if __name__ == "__main__":
    check_config()
