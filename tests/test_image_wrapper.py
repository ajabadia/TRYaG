import sys
import os
sys.path.append(os.getcwd())
import io
from PIL import Image
from src.utils.file_handler import TempFileWrapper

def test_wrapper():
    # Create a dummy image
    img = Image.new('RGB', (60, 30), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Wrap it
    wrapper = TempFileWrapper(img_byte_arr, "test.png")

    # Try to open with PIL
    try:
        img_opened = Image.open(wrapper)
        print(f"Success! Opened image: {img_opened.format} {img_opened.size}")
    except Exception as e:
        print(f"Failed to open image: {e}")

if __name__ == "__main__":
    test_wrapper()
