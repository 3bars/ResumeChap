#!/bin/bash
# ResumeChap launcher for macOS (double-clickable) and Linux.
# Finds Python 3 and starts the app.
cd "$(dirname "$0")/app" || exit 1

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python 3 is required but was not found."
  echo "Install it from https://www.python.org/downloads/ and try again."
  read -r -p "Press Enter to close…"
  exit 1
fi

"$PY" run.py "$@"
