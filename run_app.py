#!/usr/bin/env python3
"""
Lanceur direct de l'application Treasury
Évite les problèmes d'installation pip
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print(f"🔧 Python path configuré: {src_path}")

try:
    # Test import rapide
    from treasury.models import GenericDeal
    print("✅ Imports Treasury OK")
    
    # Lancer l'application Streamlit
    print("🚀 Lancement de l'application...")
    
    import subprocess
    app_path = src_path / "ui" / "app.py"
    
    # Lancer Streamlit avec le bon PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path)
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(app_path)
    ], env=env)
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("\n🔍 Vérifiez que vous êtes dans le bon dossier (SCALAR-PROJECT)")
    print("📁 Structure attendue:")
    print("  SCALAR-PROJECT/")
    print("  ├── src/treasury/")
    print("  ├── pyproject.toml")
    print("  └── run_app.py")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()