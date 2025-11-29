# path: scripts/test_new_model_import.py
import sys
import os

# Add project root to path (which is 'src' in this context if we want to simulate app behavior, but app adds 'web' to path)
# Actually app.py adds 'web' to path.
# Add project root (web) to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.db.models import VitalSignSeverityRange
    print("✅ Successfully imported VitalSignSeverityRange from src.db.models")
except ImportError as e:
    print(f"❌ Failed to import VitalSignSeverityRange: {e}")
    
try:
    from src.components.triage.triage_logic import evaluate_vital_sign
    print("✅ Successfully imported evaluate_vital_sign from src.components.triage.triage_logic")
except ImportError as e:
    print(f"❌ Failed to import from triage_logic: {e}")
