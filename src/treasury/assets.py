import base64
from pathlib import Path
import streamlit as st

# Chemin vers le répertoire racine du projet (SCALAR-PROJECT)
# __file__ est src/treasury/assets.py
# .parent -> src/treasury
# .parent.parent -> src
# .parent.parent.parent -> SCALAR-PROJECT
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Répertoire pour les assets statiques (servis par Streamlit)
STATIC_DIR = PROJECT_ROOT / "static"
IMAGES_DIR = STATIC_DIR / "images"

# Assurons-nous que le répertoire images existe
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def get_image_b64(image_name: str) -> str:
    """
    Charge une image depuis le dossier static/images et la retourne en base64.
    Retourne une chaîne vide si l'image n'est pas trouvée.
    """
    image_path = IMAGES_DIR / image_name
    if not image_path.is_file():
        # On ne met pas de st.warning ici pour ne pas polluer l'UI si l'image est optionnelle
        print(f"Warning: Image '{image_name}' not found at '{image_path}'")
        return ""
    
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    
    # Détecter le type de l'image pour le data URI
    ext = image_path.suffix.lower().replace('.', '')
    if ext == 'jpg':
        ext = 'jpeg'
    
    return f"data:image/{ext};base64,{data}"
