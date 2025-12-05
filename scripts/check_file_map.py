import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FILE_MAP_PATH = os.path.join(PROJECT_ROOT, 'docs', 'FILE_MAP.md')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

def get_files_from_map():
    mapped_files = set()
    try:
        with open(FILE_MAP_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r'\|\s*\*\*(.*?)\*\*\s*\|', line)
                if match:
                    mapped_files.add(match.group(1).replace('/', os.sep))
    except Exception as e:
        print(f"Error reading FILE_MAP.md: {e}")
    return mapped_files

def get_actual_files():
    actual_files = set()
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                actual_files.add(rel_path)
    return actual_files

def main():
    mapped = get_files_from_map()
    actual = get_actual_files()

    with open('temp_map_check.txt', 'w', encoding='utf-8') as out:
        out.write(f"Total mapped files: {len(mapped)}\n")
        out.write(f"Total actual .py files in src: {len(actual)}\n")

        missing_in_map = actual - mapped
        missing_on_disk = mapped - actual

        out.write("\n--- Files in src but NOT in FILE_MAP.md (Unmapped) ---\n")
        for f in sorted(missing_in_map):
            out.write(f"{f}\n")

        out.write("\n--- Files in FILE_MAP.md but NOT on disk (Missing/Moved) ---\n")
        for f in sorted(missing_on_disk):
            # Filter out non-src files if any were mapped
            if f.startswith('src'):
                out.write(f"{f}\n")

if __name__ == "__main__":
    main()
