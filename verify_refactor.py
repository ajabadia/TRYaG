import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

def check_file_content(filepath, search_term, should_exist=True):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if should_exist:
                if search_term in content:
                    print(f"✅ Found '{search_term}' in {filepath}")
                    return True
                else:
                    print(f"❌ '{search_term}' NOT found in {filepath}")
                    return False
            else:
                if search_term not in content:
                    print(f"✅ '{search_term}' NOT found in {filepath}")
                    return True
                else:
                    print(f"❌ Found '{search_term}' in {filepath} (Should be removed)")
                    return False
    except FileNotFoundError:
        print(f"⚠️ File not found: {filepath}")
        return False

print("Verifying Global User Menu Refactor...")

# Check app.py has render_user_menu
check_file_content("src/app.py", "render_user_menu", should_exist=True)

# Check other files do NOT have render_user_menu
files_to_check = [
    "src/ui/main_view.py",
    "src/ui/admission_view.py",
    "src/ui/boxes_view.py",
    "src/ui/waiting_room_dashboard.py",
    "src/ui/config_panel.py",
    "src/ui/audit_panel/main_panel_v2.py",
    "src/ui/admission_management_view.py"
]

all_passed = True
for f in files_to_check:
    if not check_file_content(f, "render_user_menu", should_exist=False):
        all_passed = False

if all_passed:
    print("\n🎉 Verification Successful: User Menu is global and removed from views.")
else:
    print("\n❌ Verification Failed: Issues found.")
    sys.exit(1)
