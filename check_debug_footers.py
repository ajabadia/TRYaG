import os
import re

def get_files_from_map(map_path):
    files = []
    with open(map_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('| **src/'):
                parts = line.split('|')
                if len(parts) > 2:
                    file_path = parts[1].strip().replace('**', '')
                    files.append(file_path)
    return files

def check_footer_in_file(file_path):
    full_path = os.path.abspath(file_path)
    if not os.path.exists(full_path):
        # print(f"⚠️ File not found: {file_path}")
        return False

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file is a UI file (heuristic: imports streamlit)
    if "import streamlit as st" not in content and "from streamlit" not in content:
        return False

    # Check if footer already exists
    if 'class="debug-footer"' in content:
        return False

    print(f"❌ Missing footer in: {file_path}")
    return True

def main():
    map_path = "FILE_MAP.md"
    if not os.path.exists(map_path):
        print("❌ FILE_MAP.md not found!")
        return

    files = get_files_from_map(map_path)
    print(f"Checking {len(files)} files from FILE_MAP.md for debug footers...")

    count = 0
    with open("missing_footers.txt", "w", encoding="utf-8") as f:
        for file_path in files:
            # Only process UI and Components directories
            if file_path.startswith("src/ui/") or file_path.startswith("src/components/"):
                if check_footer_in_file(file_path):
                    f.write(file_path + "\n")
                    count += 1

    print(f"\nFound {count} UI files missing debug footers. See missing_footers.txt")

if __name__ == "__main__":
    main()
