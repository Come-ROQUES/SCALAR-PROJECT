#!/usr/bin/env python3
\
\
\
\
\
\
\

import sys
import os
from pathlib import Path
import subprocess
import shutil

def main() -> int:

    this_file = Path(__file__).resolve()
    project_root = this_file.parent
    src_path = project_root / "src"
    app_path = src_path / "ui" / "app.py"
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]


    problems = []
    if not src_path.is_dir():
        problems.append(f"ERROR Dossier src introuvable: {src_path}")
    if not app_path.is_file():
        problems.append(f"ERROR app.py introuvable: {app_path}")
    if problems:
        print("\n".join(problems))
        return 1


    env = os.environ.copy()

    env["PYTHONPATH"] = str(src_path)


    streamlit_cmd += [
        "--server.fileWatcherType=watchdog",
        "--server.runOnSave=true",
        "--logger.level=debug",
    ]


    cfg_dir = project_root / ".streamlit"
    cfg_dir.mkdir(exist_ok=True)
    cfg_file = cfg_dir / "config.toml"
    if not cfg_file.exists():
        cfg_file.write_text(
            "[server]\nfileWatcherType = \"watchdog\"\nrunOnSave = true\n",
            encoding="utf-8"
        )


    print("DIAGNOSTIC LANCEMENT")
    print(f"• Python        : {sys.executable}")
    print(f"• CWD           : {Path.cwd()}")
    print(f"• Project root  : {project_root}")
    print(f"• app.py        : {app_path}")
    print(f"• PYTHONPATH    : {env.get('PYTHONPATH')}")
    print(f"• Streamlit cmd : {' '.join(streamlit_cmd)}")
    print(f"• watchdog      : {'OK' if shutil.which('python') else 'python found'}")
    print("———————————————————————————————————————————")


    try:
        return subprocess.call(streamlit_cmd, env=env, cwd=str(project_root))
    except KeyboardInterrupt:
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
