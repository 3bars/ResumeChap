#!/usr/bin/env python3
"""Cross-platform launcher for ResumeChap.

Requires only Python 3.9+ to be installed. It will:
  1. Create a local virtual environment (./.venv) on first run.
  2. Install backend dependencies into it.
  3. Build the frontend if Node.js is available and no build exists yet
     (a pre-built frontend is shipped, so Node is optional).
  4. Start the server and open your browser.

Usage:
    python run.py [--port 8000] [--no-browser]
"""
import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
import venv
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV_DIR = ROOT / ".venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_venv():
    if not venv_python().exists():
        print("[ResumeChap] Creating virtual environment…")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
    print("[ResumeChap] Installing backend dependencies…")
    subprocess.check_call(
        [str(venv_python()), "-m", "pip", "install", "-q", "--upgrade", "pip"]
    )
    subprocess.check_call(
        [str(venv_python()), "-m", "pip", "install", "-q", "-r", str(BACKEND / "requirements.txt")]
    )


def ensure_frontend_build():
    dist = FRONTEND / "dist"
    if (dist / "index.html").exists():
        return  # Pre-built frontend already present.
    npm = shutil.which("npm")
    if not npm:
        print(
            "[ResumeChap] WARNING: No frontend build found and Node.js/npm is not installed.\n"
            "             The API will run but the web UI won't be served.\n"
            "             Install Node.js and run 'npm install && npm run build' in the frontend folder,\n"
            "             or use a release that ships the pre-built frontend."
        )
        return
    print("[ResumeChap] Building frontend (first run)…")
    subprocess.check_call([npm, "install"], cwd=FRONTEND)
    subprocess.check_call([npm, "run", "build"], cwd=FRONTEND)


def open_browser_when_ready(url: str):
    def _wait():
        time.sleep(2.5)
        webbrowser.open(url)

    threading.Thread(target=_wait, daemon=True).start()


def main():
    parser = argparse.ArgumentParser(description="Run ResumeChap locally.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    ensure_venv()
    ensure_frontend_build()

    url = f"http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}"
    print(f"\n[ResumeChap] Starting server at {url}\n[ResumeChap] Press Ctrl+C to stop.\n")

    if not args.no_browser:
        open_browser_when_ready(url)

    env = dict(os.environ)
    subprocess.call(
        [
            str(venv_python()),
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ],
        cwd=BACKEND,
        env=env,
    )


if __name__ == "__main__":
    main()
