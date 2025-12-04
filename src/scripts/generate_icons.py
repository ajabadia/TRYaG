import os
from PIL import Image

def generate_icons():
    source_path = r"src/assets/icons/logo.png"
    dest_dir = r"src/static/icons"
    
    if not os.path.exists(source_path):
        print(f"Error: Source image not found at {source_path}")
        return

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created destination directory: {dest_dir}")

    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    shortcuts = ["shortcut-admission.png", "shortcut-triage.png", "shortcut-boxes.png"]

    try:
        with Image.open(source_path) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Generate standard icons
            for size in sizes:
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                filename = f"icon-{size}x{size}.png"
                dest_path = os.path.join(dest_dir, filename)
                resized_img.save(dest_path, "PNG")
                print(f"Generated: {dest_path}")

            # Generate shortcut icons (using 96x96 size)
            shortcut_img = img.resize((96, 96), Image.Resampling.LANCZOS)
            for shortcut_name in shortcuts:
                dest_path = os.path.join(dest_dir, shortcut_name)
                shortcut_img.save(dest_path, "PNG")
                print(f"Generated shortcut: {dest_path}")

        print("All icons generated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_icons()
