import os

def get_indentation(line):
    return len(line) - len(line.lstrip())

def apply_footer(file_path):
    full_path = os.path.abspath(file_path)
    if not os.path.exists(full_path):
        print(f"⚠️ File not found: {file_path}")
        return False

    with open(full_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return False

    # Find the last non-empty line
    last_line_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            last_line_idx = i
            break
    
    if last_line_idx == -1:
        return False

    last_line = lines[last_line_idx]
    indent = get_indentation(last_line)
    indent_str = " " * indent
    
    # Prepare footer
    # We use a generic div class 'debug-footer'
    footer_code = f'\n{indent_str}st.markdown(\'<div class="debug-footer">{file_path.replace(os.sep, "/")}</div>\', unsafe_allow_html=True)\n'

    # Append
    with open(full_path, 'a', encoding='utf-8') as f:
        f.write(footer_code)
    
    print(f"✅ Applied footer to: {file_path}")
    return True

def main():
    if not os.path.exists("missing_footers.txt"):
        print("❌ missing_footers.txt not found!")
        return

    with open("missing_footers.txt", 'r', encoding='utf-8') as f:
        files = [line.strip() for line in f if line.strip()]

    print(f"Applying footers to {len(files)} files...")
    
    count = 0
    for file_path in files:
        if apply_footer(file_path):
            count += 1
            
    print(f"\n🎉 Finished! Applied footers to {count} files.")

if __name__ == "__main__":
    main()
