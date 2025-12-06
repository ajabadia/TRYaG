
import os

def main():
    file_path = "src/components/triage/input_form.py"
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Lines to remove: 292 to 412 (1-based)
    # Indices: 291 to 411 (0-based)
    # We want [0..290] + [412..END]
    
    start_cut_idx = 291
    end_cut_idx = 412 # The first line AFTER the cut (Line 413)
    
    # Verify content to be sure
    print(f"Line 292 (Start Cut): {lines[start_cut_idx].strip()}")
    print(f"Line 412 (End Cut): {lines[end_cut_idx-1].strip()}")
    print(f"Line 413 (Resume): {lines[end_cut_idx].strip()}")
    
    if "Legacy code block start" in lines[start_cut_idx] and "Debug Footer removed" in lines[end_cut_idx-1]:
        print("✅ Markers match. Proceeding with cut.")
        new_lines = lines[:start_cut_idx] + lines[end_cut_idx:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("✅ File updated.")
    else:
        print("❌ Markers do NOT match. Aborting.")
        print(f"Expected 'Legacy...' got: {lines[start_cut_idx]}")
        print(f"Expected 'Debug...' got: {lines[end_cut_idx-1]}")

if __name__ == "__main__":
    main()
