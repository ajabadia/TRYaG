import os
import sys
import google.generativeai as genai

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def load_env_manual():
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    if key == "GOOGLE_API_KEY":
                        os.environ["GOOGLE_API_KEY"] = value.strip('"').strip("'")
                        print("API Key loaded manually.")
                        return True
    except Exception as e:
        print(f"Error loading .env: {e}")
    return False

def test_model(model_name):
    print(f"\n--- Testing model: {model_name} ---")
    # Hardcoded key for testing
    api_key = "AIzaSyC8sV0M56YzCDL-O5n6m5emMLmtHjdxN3s"
    if not api_key:
        print("Error: GOOGLE_API_KEY not found.")
        return

    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, are you working?")
        
        if response.parts:
            print(f"Success! Response: {response.text}")
        else:
            print(f"Error: Empty response parts.")
            if response.prompt_feedback:
                print(f"Feedback: {response.prompt_feedback}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        load_env_manual()
        
    test_model("gemini-2.5-flash")
    test_model("gemini-2.0-flash")
