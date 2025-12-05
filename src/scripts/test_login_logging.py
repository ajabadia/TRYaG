# path: src/scripts/test_login_logging.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.repositories.login_logs import get_login_logs_repository
from datetime import datetime

def test_logging():
    print("Testing LoginLogsRepository...")
    try:
        repo = get_login_logs_repository()
        print(f"Repository initialized: {repo}")
        
        print("Attempting to log a test login...")
        log_id = repo.log_login(
            user_id="TEST_USER_ID",
            username="test_script_user",
            success=True,
            ip_address="127.0.0.1",
            details={"source": "test_script"}
        )
        print(f"✅ Log created with ID: {log_id}")
        
        # Verify it exists
        from db.connection import get_database
        db = get_database()
        doc = db.login_logs.find_one({"_id": log_id})
        if doc:
            print("✅ Document found in MongoDB:")
            print(doc)
        else:
            print("❌ Document NOT found immediately after insertion.")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logging()
