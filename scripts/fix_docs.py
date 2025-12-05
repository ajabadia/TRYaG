
import os

file_path = r"c:\Users\ajaba\Downloads\master\ftm\piloto ABD\nuevo\web\docs\TECHNICAL.md"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the second occurrence of the header
header = "# Documentación Técnica - Asistente de Triaje IA"
first_found = False
cut_index = -1

for i, line in enumerate(lines):
    if header in line:
        if not first_found:
            first_found = True
        else:
            cut_index = i
            break

if cut_index != -1:
    print(f"Found duplicate at line {cut_index + 1}. Truncating...")
    new_content = lines[:cut_index]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    print("File truncated successfully.")
else:
    print("No duplicate header found.")
