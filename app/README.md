# ResumeChap — Self-Hosted Resume Manager (Part 1)

A local, self-hosted web app to **add, curate, generate, catalog, tag, revise, and
delete** multiple versions of your resume — one per role/track (e.g. a *Cloud*
resume, a *Linux* resume, a *DevOps* resume). Optionally, an AI engine can
summarize the differences between any two versions.

Everything runs **locally on your machine**. Your data lives in a local SQLite
database and never leaves your computer (except AI requests you explicitly enable).

---

## Quick start

You only need **Python 3.9+** installed. The web UI is pre-built and shipped, so
Node.js is **not** required to run the app.

### macOS
- Double-click **`start.command`** in the project root, **or** run in a terminal:
  ```bash
  ./start.sh
  ```

### Windows
- Double-click **`start.bat`**, **or** run in a terminal:
  ```bat
  start.bat
  ```

### Linux
```bash
./start.sh
```

On first launch it creates a local virtual environment, installs dependencies,
starts the server, and opens `http://localhost:8000` in your browser.

To stop the app, press `Ctrl+C` in the terminal (or close the window).

Options: `python app/run.py --port 9000 --no-browser`

---

## Features

- **Catalog** — browse all your resumes, search by text, and filter by tag.
- **Resumes & versions** — each resume keeps an ordered version history so you can
  revise over time, preview any version, and roll back by comparing.
- **Tagging** — organize resumes with free-form tags.
- **resume-engine** — author content in markdown, or **import** an existing
  resume from **PDF, DOCX, TXT, or Markdown** to pre-fill the editor.
- **ai-engine (optional)** — enable AI in *Settings* to generate a written summary
  of what changed between two versions. Supported providers:
  - **Abacus.AI** (no API key needed — uses the built-in environment)
  - **OpenAI**
  - **Anthropic (Claude)**
  - **Google Gemini**
  - **Microsoft Copilot / Azure OpenAI**
  - When AI is disabled you still get a full plain-text diff.

---

## Where your data lives

| What | Location (macOS/Linux) | Location (Windows) |
|------|------------------------|--------------------|
| Database | `~/.resumechap/resumechap.db` | `%APPDATA%\ResumeChap\resumechap.db` |
| AI settings / keys | `~/.resumechap/ai_settings.json` | `%APPDATA%\ResumeChap\ai_settings.json` |

API keys are stored **only** on your machine and are never committed to the repo.
You can override the data directory with the `RESUMECHAP_DATA_DIR` environment
variable.

---

## For developers

### Run the backend and frontend separately (hot reload)
```bash
# Terminal 1 — backend
cd app/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 — frontend (proxies /api to the backend on :8000)
cd app/frontend
npm install
npm run dev        # http://localhost:5173
```

### Rebuild the shipped frontend
```bash
cd app/frontend
npm install
npm run build      # outputs to app/frontend/dist (served by the backend)
```

### Project layout
```
app/
├── backend/          FastAPI + SQLite
│   ├── main.py           API routes + serves the built frontend
│   ├── models.py         SQLAlchemy models (Resume, ResumeVersion, Tag)
│   ├── schemas.py        Pydantic request/response models
│   ├── crud.py           Database operations
│   ├── resume_engine.py  File import/parsing (PDF/DOCX/TXT/MD)
│   ├── ai_engine.py      Optional, pluggable AI provider layer
│   └── requirements.txt
├── frontend/         React (Vite) web UI  (dist/ is committed)
└── run.py            Cross-platform launcher
```

### Building a standalone executable (optional)
For a true one-file binary with no Python dependency, build per-OS with
[PyInstaller](https://pyinstaller.org/) on that OS:
```bash
cd app/backend
pip install pyinstaller
pyinstaller --onefile --add-data "../frontend/dist:frontend/dist" main.py
```
(Windows uses `;` instead of `:` in `--add-data`.)

---

## API

Interactive API docs are available at `http://localhost:8000/api/docs` while the
app is running.
