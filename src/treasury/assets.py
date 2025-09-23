import base64
from pathlib import Path
import streamlit as st






PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


STATIC_DIR = PROJECT_ROOT / "static"
IMAGES_DIR = STATIC_DIR / "images"


IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def get_image_b64(image_name: str) -> str:
    \
\
\
\
    image_path = IMAGES_DIR / image_name
    if not image_path.is_file():

        print(f"Warning: Image '{image_name}' not found at '{image_path}'")
        return ""

    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")


    ext = image_path.suffix.lower().replace('.', '')
    if ext == 'jpg':
        ext = 'jpeg'

    return f"data:image/{ext};base64,{data}"
