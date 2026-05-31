# MNEMO — AI-Assisted Notepad App: Documentation Index

> **App Name (working title): MNEMO**
> *From Mnemosyne — Greek goddess of memory and remembrance.*

---

## How to Use This Documentation Suite

This documentation is designed to be consumed by **any LLM agent** (Claude, Copilot, Cursor, Deepseek, etc.) assisting you at any phase of development. Always paste the relevant document(s) into the LLM's context along with your specific prompt. The LLM will know exactly what phase you're in, what's already built, and what to do next.

---

## Document Map

| # | File | Purpose |
|---|------|---------|
| 00 | `00_PROJECT_INDEX.md` | This file — navigation and orientation |
| 01 | `01_PRODUCT_REQUIREMENTS.md` | Full PRD: features, user stories, functional/non-functional requirements |
| 02 | `02_UI_WIREFRAMES_AND_THEMES.md` | Wireframe descriptions for every screen + 3 theme specs |
| 03 | `03_ARCHITECTURE.md` | System architecture, data models, API design, encryption strategy |
| 04 | `04_DEVELOPMENT_ROADMAP.md` | Phased dev plan (Phase 0–6), dependencies, commands |
| 05 | `05_LLM_AGENT_CONTEXT.md` | Quick-load context card for LLM agents — paste this first |
| 06 | `06_DATABASE_SCHEMA.md` | Full SQLite/Turso schema with migration notes |
| 07 | `07_API_REFERENCE.md` | All Flask API endpoints, request/response shapes |
| 08 | `08_FRONTEND_COMPONENT_TREE.md` | React component hierarchy and state management |

---

## Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite, TailwindCSS, Three.js / p5.js |
| Editor | TipTap (ProseMirror-based rich text) |
| Backend | Python 3.11+, Flask, Flask-JWT-Extended |
| ORM | SQLAlchemy (local dev) → Turso (libsql) for production |
| Database | SQLite locally → Turso (LibSQL) in production |
| Auth | JWT (access + refresh tokens) |
| Encryption | AES-256-GCM via Python `cryptography` lib (server-side) + optional client-side |
| Search | SQLite FTS5 (local) → Turso FTS (prod) |
| Deployment | Render (Flask backend + Vite static frontend) |
| Dev Tools | VSCode + GitHub Copilot + Cursor |

---

## Quick Dev Commands Reference

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
flask db init && flask db migrate && flask db upgrade
flask run --debug

# Frontend
cd frontend && npm install
npm run dev

# Run both (from root)
# Use two terminals or install concurrently:
npx concurrently "cd backend && flask run" "cd frontend && npm run dev"
```

---

## Current Phase Tracker

> **Update this manually as you progress through the roadmap.**

- [ ] Phase 0 — Environment Setup
- [ ] Phase 1 — Backend Core (Auth, Notes CRUD, Encryption)
- [ ] Phase 2 — Frontend Core (Editor, Timeline, Search)
- [ ] Phase 3 — Themes (Space / Canvas / Calendar)
- [ ] Phase 4 — Social Features (Sharing, Blog, Network)
- [ ] Phase 5 — Production Migration (Turso + Render)
- [ ] Phase 6 — Polish & Launch

---

*Last updated: Initial generation. Update as app evolves.*
