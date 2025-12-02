
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from db import get_database

def extract_clinical_options():
    with open('clinical_options_dump.txt', 'w', encoding='utf-8') as f:
        try:
            db = get_database()
            collection = db["clinical_options"]
            
            # Get all options sorted by category and name
            options = list(collection.find().sort([("category", 1), ("name", 1)]))
            
            f.write("=== CLINICAL OPTIONS ANNEX ===\n")
            
            current_category = None
            for opt in options:
                category = opt.get('category', 'Uncategorized')
                # Try 'text' first, then 'value', then 'name'
                name = opt.get('text') or opt.get('value') or opt.get('name') or 'Unknown'
                
                if category != current_category:
                    f.write(f"\n## {category}\n")
                    current_category = category
                
                f.write(f"- {name}\n")
                
        except Exception as e:
            f.write(f"Error extracting options: {e}\n")

if __name__ == "__main__":
    extract_clinical_options()
