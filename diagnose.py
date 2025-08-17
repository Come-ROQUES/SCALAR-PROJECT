#!/usr/bin/env python3
"""
Diagnostic de la structure du projet Treasury
"""

import os
from pathlib import Path

def diagnose_project():
    print("🔍 DIAGNOSTIC DU PROJET TREASURY")
    print("=" * 50)
    
    # Vérifier le dossier courant
    current_dir = Path.cwd()
    print(f"📁 Dossier courant: {current_dir}")
    
    # Vérifier les fichiers essentiels
    essential_files = [
        "pyproject.toml",
        "src/treasury/__init__.py",
        "src/treasury/models.py",
        "src/treasury/pnl.py",
        "src/ui/app.py"
    ]
    
    print("\n📋 FICHIERS ESSENTIELS:")
    all_present = True
    for file in essential_files:
        file_path = current_dir / file
        status = "✅" if file_path.exists() else "❌"
        print(f"  {status} {file}")
        if not file_path.exists():
            all_present = False
    
    # Vérifier la structure des dossiers
    print("\n📂 STRUCTURE DES DOSSIERS:")
    expected_dirs = [
        "src",
        "src/treasury", 
        "src/treasury/utils",
        "src/treasury/io",
        "src/ui"
    ]
    
    for dir_path in expected_dirs:
        full_path = current_dir / dir_path
        status = "✅" if full_path.is_dir() else "❌"
        print(f"  {status} {dir_path}/")
    
    # Lister les fichiers dans src/treasury
    treasury_dir = current_dir / "src" / "treasury"
    if treasury_dir.exists():
        print(f"\n📄 FICHIERS DANS {treasury_dir}:")
        for file in sorted(treasury_dir.glob("*.py")):
            print(f"  ✅ {file.name}")
    
    # Recommandations
    print("\n🔧 RECOMMANDATIONS:")
    if not all_present:
        print("  ❌ Fichiers manquants détectés")
        print("  👉 Créez les fichiers manqués selon la structure modulaire")
    
    if not (current_dir / "pyproject.toml").exists():
        print("  ❌ pyproject.toml manquant")
        print("  👉 Créez ce fichier pour permettre l'installation pip")
    
    if all_present:
        print("  ✅ Structure complète détectée")
        print("  👉 Vous pouvez lancer: python run_app.py")
    
    print("\n🚀 COMMANDES SUGGÉRÉES:")
    print("  # Installation classique:")
    print("  pip install -e .")
    print("  streamlit run src/ui/app.py")
    print()
    print("  # OU lancement direct:")
    print("  python run_app.py")

if __name__ == "__main__":
    diagnose_project()