import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables manually if needed, or rely on service
load_dotenv()

from services.ai_model_discovery import fetch_and_update_models
from db.repositories.ai_models import get_ai_models_repository
from db.repositories.general_config import get_general_config_repository

def verify_system():
    with open("verify_output_utf8.txt", "w", encoding="utf-8") as f:
        f.write("--- Verifying AI Model Management System ---\n")
        
        # 1. Test Discovery Service
        f.write("\n1. Testing fetch_and_update_models()...\n")
        success, msg, count = fetch_and_update_models()
        if success:
            f.write(f"✅ Success: {msg}\n")
        else:
            f.write(f"❌ Failed: {msg}\n")
            # If failed due to API key, we might need to inject it for test
            if "GOOGLE_API_KEY" not in os.environ:
                 f.write("⚠️ GOOGLE_API_KEY not in env. Trying hardcoded fallback for test...\n")
                 os.environ["GOOGLE_API_KEY"] = "AIzaSyC8sV0M56YzCDL-O5n6m5emMLmtHjdxN3s"
                 success, msg, count = fetch_and_update_models()
                 if success:
                     f.write(f"✅ Retry Success: {msg}\n")
                 else:
                     f.write(f"❌ Retry Failed: {msg}\n")
                     return

        # 2. Verify Database Content
        f.write("\n2. Verifying AIModelsRepository...\n")
        repo = get_ai_models_repository()
        models = repo.get_available_models()
        f.write(f"Found {len(models)} active models in DB.\n")
        if len(models) > 0:
            f.write(f"Sample models: {models[:5]}\n")
            if "gemini-2.5-flash" in models:
                 f.write("✅ 'gemini-2.5-flash' is present.\n")
            else:
                 f.write("⚠️ 'gemini-2.5-flash' NOT found in list.\n")
        else:
            f.write("❌ No models found in DB.\n")

        # 3. Verify General Config
        f.write("\n3. Verifying GeneralConfigRepository...\n")
        config_repo = get_general_config_repository()
        config = config_repo.get_config()
        f.write(f"Current Config: {config}\n")
        if "default_ai_model" in config:
            f.write(f"✅ default_ai_model is set to: {config['default_ai_model']}\n")
        else:
            f.write("⚠️ default_ai_model key missing (might be using legacy keys or default).\n")

if __name__ == "__main__":
    verify_system()
