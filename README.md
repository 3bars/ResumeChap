# ResumeChap

**Tools to manage your resumes and make job applications easier.**

ResumeChap is being built in two parts:

1. **Resume Manager (self-hosted web app)** — ✅ *available now* — a local app to
   add, curate, catalog, tag, revise, compare, and delete multiple versions of
   your resume (e.g. a *Cloud* resume, a *DevOps* resume, a *Linux* resume). It
   includes an optional AI engine that summarizes the differences between resume
   versions. **See [`app/README.md`](app/README.md) to get started.**
2. **Browser plugin** — 🚧 *planned* — a browser extension that helps auto-fill
   repetitive job application forms across job boards and ATS platforms, using
   the resumes you manage in Part 1.

---

## Part 1 — Resume Manager (self-hosted)

A local, privacy-first web application. Everything runs on your machine; your
data lives in a local SQLite database and never leaves your computer (except AI
requests you explicitly enable).

### Quick start

You only need **Python 3.9+**. The web UI ships pre-built, so Node.js is not
required to run it.

- **macOS:** double-click `start.command` (or run `./start.sh`)
- **Windows:** double-click `start.bat`
- **Linux:** run `./start.sh`

On first launch it sets up a local environment, starts the server, and opens
`http://localhost:8000` in your browser.

### Features

- **Catalog** with text search and tag filtering
- **Multiple resumes**, each with a full **version history** (revise, preview, roll back)
- **Tagging** for organization
- **resume-engine** — write in markdown or **import** from PDF / DOCX / TXT / MD
- **ai-engine (optional)** — AI summaries of the differences between two versions,
  with pluggable providers: **Abacus.AI, OpenAI, Anthropic, Google Gemini,
  Microsoft Copilot / Azure OpenAI**. Falls back to a plain text diff when disabled.

Full documentation, developer setup, and data locations are in
[`app/README.md`](app/README.md).

---

## Part 2 — Browser plugin (planned)

- **Smart auto-fill** of common job application fields.
- **Resume-aware suggestions** drawing from the resumes managed in Part 1.
- **Cross-site support** across major job boards and ATS platforms.
- **Privacy-first** — your data stays local.

> 🚧 In early development. Details will be added as the plugin matures.

---

## Prerequisites

- **Part 1:** Python 3.9+ (Node.js only needed for frontend development).
- **Part 2:** A Chromium-based browser (Chrome, Edge, Brave) or Firefox.

## Contributing

Contributions are welcome! Please open an issue to discuss any significant
changes before submitting a pull request.

## License

This project is licensed under the terms of the **GNU General Public License
v2.0 (GPLv2)**. See the [LICENSE](LICENSE) file for the full license text.
