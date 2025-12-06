import sys
import os
import traceback

# Redirect stdout/stderr to file
sys.stdout = open('debug_output.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

# Add src to path
web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(web_root)
sys.path.append(os.path.join(web_root, 'src'))

print("--- SYS PATH ---")
for p in sys.path:
    print(p)
print("----------------")

try:
    print("Importing TriageService...")
    from src.services.triage_service import TriageService
    print("✅ TriageService imported.")
except Exception as e:
    print(f"❌ Failed to import TriageService: {e}")
    traceback.print_exc()

try:
    print("\nImporting PredictiveService...")
    from src.services.predictive_service import PredictiveService
    print("✅ PredictiveService imported.")
except Exception as e:
    print(f"❌ Failed to import PredictiveService: {e}")
    traceback.print_exc()

sys.stdout.close()
