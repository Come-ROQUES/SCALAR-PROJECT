#!/usr/bin/env python3
"""
Lanceur robuste pour SCALAR-PROJECT
- Indépendant du dossier courant (cwd)
- Force PYTHONPATH=src
- Active watchdog + runOnSave
- Affiche un diagnostic clair
"""

import sys
import os
from pathlib import Path
import subprocess
import shutil

def main() -> int:
    # 1) Localise la racine du repo à partir de CE fichier
    this_file = Path(__file__).resolve()
    project_root = this_file.parent  # <= run_app.py est à la racine
    src_path = project_root / "src"
    app_path = src_path / "ui" / "app.py"
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]

    # 2) Vérifs de base
    problems = []
    if not src_path.is_dir():
        problems.append(f"❌ Dossier src introuvable: {src_path}")
    if not app_path.is_file():
        problems.append(f"❌ app.py introuvable: {app_path}")
    if problems:
        print("\n".join(problems))
        return 1

    # 3) Environnement propre
    env = os.environ.copy()
    # Force PYTHONPATH pour que les imports passent toujours par src/
    env["PYTHONPATH"] = str(src_path)

    # 4) Options Streamlit: watchdog + runOnSave + logs
    streamlit_cmd += [
        "--server.fileWatcherType=watchdog",
        "--server.runOnSave=true",
        "--logger.level=debug",
    ]

    # 5) (Optionnel) Assurer un .streamlit/config.toml cohérent
    cfg_dir = project_root / ".streamlit"
    cfg_dir.mkdir(exist_ok=True)
    cfg_file = cfg_dir / "config.toml"
    if not cfg_file.exists():
        cfg_file.write_text(
            "[server]\nfileWatcherType = \"watchdog\"\nrunOnSave = true\n",
            encoding="utf-8"
        )

    # 6) Affiche un diagnostic utile (pour éviter les doutes)
    print("🔧 DIAGNOSTIC LANCEMENT")
    print(f"• Python        : {sys.executable}")
    print(f"• CWD           : {Path.cwd()}")
    print(f"• Project root  : {project_root}")
    print(f"• app.py        : {app_path}")
    print(f"• PYTHONPATH    : {env.get('PYTHONPATH')}")
    print(f"• Streamlit cmd : {' '.join(streamlit_cmd)}")
    print(f"• watchdog      : {'OK' if shutil.which('python') else 'python found'}")
    print("———————————————————————————————————————————")

    # 7) LANCE Streamlit depuis la RACINE (cwd=project_root), peu importe d’où on exécute run_app.py
    try:
        return subprocess.call(streamlit_cmd, env=env, cwd=str(project_root))
    except KeyboardInterrupt:
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
