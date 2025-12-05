import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FILE_MAP_PATH = os.path.join(PROJECT_ROOT, 'docs', 'FILE_MAP.md')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

def get_existing_map():
    file_map = {}
    header_lines = []
    try:
        with open(FILE_MAP_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        in_table = False
        for line in lines:
            if line.strip().startswith('| **'):
                in_table = True
                # Parse row
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    # parts[0] is empty, parts[1] is filename, parts[2] is description, parts[3] is invoked by, parts[4] is status
                    filename_raw = parts[1]
                    # Extract filename from **filename**
                    match = re.search(r'\*\*(.*?)\*\*', filename_raw)
                    if match:
                        filename = match.group(1).replace('/', os.sep)
                        description = parts[2]
                        invoked_by = parts[3] if len(parts) > 3 else "N/A"
                        status = parts[4] if len(parts) > 4 else "Activo"
                        file_map[filename] = {
                            'description': description,
                            'invoked_by': invoked_by,
                            'status': status
                        }
            elif not in_table and not line.strip().startswith('|'):
                header_lines.append(line)
            elif line.strip().startswith('| :---'):
                pass # Skip separator
            elif line.strip().startswith('| Ruta'):
                pass # Skip header
                
    except Exception as e:
        print(f"Error reading FILE_MAP.md: {e}")
        # Default header if file doesn't exist or error
        header_lines = [
            "# Mapa de Archivos del Proyecto\n",
            "\n",
            "Este documento lista los archivos principales del proyecto, su propósito y su estado.\n",
            "\n"
        ]
    return file_map, header_lines

def get_actual_files():
    actual_files = set()
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                actual_files.add(rel_path)
    return actual_files

def main():
    existing_map, header_lines = get_existing_map()
    actual_files = get_actual_files()
    
    # Identify missing and new
    existing_filenames = set(existing_map.keys())
    
    # We need to handle path separators carefully. 
    # The map might use forward slashes, os might use backslashes.
    # We normalized to os.sep in get_existing_map.
    
    files_to_write = []
    
    # Add existing files that still exist
    for f in existing_filenames:
        if f in actual_files:
            files_to_write.append((f, existing_map[f]))
        elif f.startswith('src'):
            print(f"Removing missing file: {f}")
        else:
            # Keep non-src files (like deprecated ones if they are in the map)
             files_to_write.append((f, existing_map[f]))

    # Add new files
    for f in actual_files:
        if f not in existing_filenames:
            print(f"Adding new file: {f}")
            files_to_write.append((f, {
                'description': "Pendiente de descripción.",
                'invoked_by': "Pendiente",
                'status': "Activo"
            }))
            
    # Sort by filename
    files_to_write.sort(key=lambda x: x[0])
    
    # Write back to FILE_MAP.md
    with open(FILE_MAP_PATH, 'w', encoding='utf-8') as f:
        for line in header_lines:
            f.write(line)
            
        f.write("| Ruta del Archivo | Descripción | Invocado Por | Estado |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        
        for filename, data in files_to_write:
            # Ensure forward slashes for markdown
            display_filename = filename.replace('\\', '/')
            f.write(f"| **{display_filename}** | {data['description']} | {data['invoked_by']} | {data['status']} |\n")
            
    print(f"Successfully updated FILE_MAP.md with {len(files_to_write)} files.")

if __name__ == "__main__":
    main()
