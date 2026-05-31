# MNEMO — LLM Agent Context Card
## Document: 05_LLM_AGENT_CONTEXT.md

---

> **PURPOSE:** Paste this document (or the relevant section) into any LLM's context window to quickly orient it to the MNEMO project. Combine with specific phase instructions from `04_DEVELOPMENT_ROADMAP.md` and the relevant schema/API docs.

---

## PROJECT SNAPSHOT

**App Name:** MNEMO (working title)
**Type:** Web-based notepad / diary / rich text editor
**Stack:**
- Frontend: React 18 + Vite + TailwindCSS + Three.js + TipTap
- Backend: Python 3.11 + Flask + SQLAlchemy + Flask-JWT-Extended
- Database: SQLite locally → Turso (LibSQL) in production
- Deployment: Render (Flask + Vite static)
- Auth: JWT (access 15min, refresh 7 days)
- Encryption: AES-256-GCM (server-side, `cryptography` lib)

**Repo structure:**
```
mnemo/
├── backend/   (Flask app)
├── frontend/  (React/Vite app)
└── docs/      (this documentation)
```

---

## KEY DESIGN DECISIONS (Do not deviate without asking)

1. **App factory pattern** for Flask — `create_app()` in `app/__init__.py`
2. **SQLAlchemy ORM** — no raw SQL except for FTS5 search queries
3. **AES-256-GCM encryption** — always use `app/utils/encryption.py` — never skip encryption when saving notes
4. **Zustand** for frontend state — not Redux, not Context alone
5. **TipTap** for rich text — not Quill, not Draft.js
6. **Three.js** for Space theme — load lazily (React.lazy)
7. **JWT in Authorization header** — not cookies
8. **Soft delete** — notes have `deleted_at` column, never hard-delete
9. **FTS5** for search — not LIKE queries
10. **Note visibility:** `private` | `unlisted` | `public` only

---

## WHAT'S BEEN BUILT (update this as you progress)

> Developer: Update this section at the end of each phase so any LLM you switch to knows what's done.

```
[ ] Phase 0 — Environment Setup        COMPLETE / IN PROGRESS / NOT STARTED
[ ] Phase 1 — Backend Core             COMPLETE / IN PROGRESS / NOT STARTED
[ ] Phase 2 — Frontend Core            COMPLETE / IN PROGRESS / NOT STARTED
[ ] Phase 3 — Timeline Themes          COMPLETE / IN PROGRESS / NOT STARTED
[ ] Phase 4 — Social Features          COMPLETE / IN PROGRESS / NOT STARTED
[ ] Phase 5 — Production Migration     COMPLETE / IN PROGRESS / NOT STARTED
[ ] Phase 6 — Polish & Launch          COMPLETE / IN PROGRESS / NOT STARTED
```

**Current blockers / decisions pending:**
- (Developer: list any open questions or blockers here)

---

## HOW TO USE THIS DOCUMENT IN PROMPTS

### Starting a new LLM session (copy-paste template):

```
I'm building an app called MNEMO — a web-based encrypted notepad with timeline visualization and social features.

Stack: Flask + SQLAlchemy (SQLite locally / Turso in prod) backend, React 18 + Vite + TipTap + Three.js frontend, JWT auth, AES-256-GCM encryption.

[PASTE RELEVANT SECTION FROM THIS DOC]

I am currently in Phase [X]. Here is what I need help with:
[YOUR SPECIFIC TASK]

Please follow the patterns established in the architecture doc and do not deviate from the tech stack choices.
```

---

## COMMON TASKS & WHERE TO LOOK

| Task | Primary Doc | Section |
|------|-------------|---------|
| Add a new Flask route | `07_API_REFERENCE.md` | Blueprint patterns |
| Add a new DB model | `06_DATABASE_SCHEMA.md` | Model definitions |
| Implement a new React page | `08_FRONTEND_COMPONENT_TREE.md` | Component tree |
| Work on encryption | `03_ARCHITECTURE.md` | Section 4 |
| Work on search | `03_ARCHITECTURE.md` | Section 5 |
| Work on Space theme | `02_UI_WIREFRAMES_AND_THEMES.md` | Theme 1 |
| Work on Calendar theme | `02_UI_WIREFRAMES_AND_THEMES.md` | Theme 3 |
| Understand data models | `06_DATABASE_SCHEMA.md` | Full schema |
| Deploy to Render | `04_DEVELOPMENT_ROADMAP.md` | Phase 5 |
| Switch to Turso | `04_DEVELOPMENT_ROADMAP.md` | Phase 5.1-5.3 |

---

## CRITICAL CONSTRAINTS FOR LLM AGENTS

1. **Never store plaintext note bodies in the `body` column** — always use `encrypt()` before writing, `decrypt()` after reading
2. **Never return passwords or tokens in API responses** beyond login/register
3. **All protected routes need `@jwt_required()`**
4. **Social features (feed, reactions, comments) only work on `public` notes** — enforce this server-side
5. **Search FTS queries must scope to `user_id`** for private notes — never leak other users' content
6. **Soft delete only** — check `deleted_at IS NULL` in all queries
7. **Generate slugs from titles** using `python-slugify`, ensure uniqueness with a UUID suffix if needed
8. **The Three.js scene MUST be cleaned up** (dispose geometries, materials, renderer) when unmounting Space theme component

---

## NAMING CONVENTIONS

### Backend (Python)
- Models: PascalCase (`NoteVersion`, `UserFollow`)
- Functions: snake_case (`get_note_by_id`, `encrypt_body`)
- Routes: kebab-case URLs (`/api/notes/:id/versions`)
- Variables: snake_case

### Frontend (JavaScript/React)
- Components: PascalCase (`NoteEditor`, `SpaceTimeline`)
- Hooks: camelCase with `use` prefix (`useAutoSave`, `useSearch`)
- Store slices: camelCase (`authStore`, `themeStore`)
- API functions: camelCase (`fetchNotes`, `createNote`)
- CSS classes: Tailwind utility classes; custom: kebab-case

---

## ENVIRONMENT VARIABLES REFERENCE

### Backend `.env`
```
FLASK_APP=run.py
FLASK_ENV=development|production
SECRET_KEY=<32-byte hex>
JWT_SECRET_KEY=<32-byte hex>
ENCRYPTION_KEY=<32-byte hex>
DATABASE_URL=sqlite:///mnemo_dev.db | libsql+http://[org]-[db].turso.io?authToken=[token]
FRONTEND_URL=http://localhost:5173 | https://your-app.onrender.com
```

### Frontend `.env`
```
VITE_API_URL=http://localhost:5000 | https://mnemo-backend.onrender.com
```

---

## ERROR RESPONSE FORMAT (Always consistent)

```json
{
  "error": "Human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "details": {}
}
```

## SUCCESS RESPONSE FORMAT

```json
{
  "data": { ... },
  "message": "Optional success message",
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 143
  }
}
```
