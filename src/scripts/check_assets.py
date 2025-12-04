import os
import re
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def check_assets():
    """
    Scans the codebase for asset references and verifies their existence.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    src_dir = os.path.join(project_root, "src")
    
    print(f"🔍 Scanning for asset references in {src_dir}...")
    print(f"📂 Project Root: {project_root}")
    
    missing_assets = []
    checked_count = 0
    
    # Regex for get_icon_path usage
    icon_pattern = re.compile(r'get_icon_path\s*\(\s*["\']([^"\']+)["\']\s*\)')
    
    # Regex for general asset paths (simple heuristic)
    asset_pattern = re.compile(r'["\'](src/assets/[^"\']+)["\']')
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Check icons
                for match in icon_pattern.finditer(content):
                    icon_name = match.group(1)
                    # Construct expected path
                    expected_path = os.path.join(project_root, "src", "assets", "icons", f"{icon_name}.svg")
                    checked_count += 1
                    if not os.path.exists(expected_path):
                        # Try logos folder as fallback
                        logo_path = os.path.join(project_root, "src", "assets", "logos", f"{icon_name}.svg")
                        if os.path.exists(logo_path):
                            continue # It exists in logos, so it's fine (or we should warn?)
                            
                        missing_assets.append({
                            "type": "icon",
                            "name": icon_name,
                            "file": os.path.relpath(file_path, project_root),
                            "expected": expected_path
                        })

                # Check other assets
                for match in asset_pattern.finditer(content):
                    asset_rel_path = match.group(1)
                    # Fix path separators for Windows
                    asset_rel_path_os = asset_rel_path.replace("/", os.sep)
                    expected_path = os.path.join(project_root, asset_rel_path_os)
                    
                    checked_count += 1
                    if not os.path.exists(expected_path):
                         missing_assets.append({
                            "type": "file",
                            "name": asset_rel_path,
                            "file": os.path.relpath(file_path, project_root),
                            "expected": expected_path
                        })
                        
            except Exception as e:
                print(f"⚠️ Error reading {file}: {e}")

    print(f"\n✅ Checked {checked_count} references.")
    
    if missing_assets:
        print(f"\n❌ Found {len(missing_assets)} missing assets:")
        for missing in missing_assets:
            print(f"  - [{missing['type'].upper()}] '{missing['name']}' referenced in {missing['file']}")
            print(f"    Expected at: {missing['expected']}")
    else:
        print("\n🎉 All asset references appear valid!")

if __name__ == "__main__":
    check_assets()
