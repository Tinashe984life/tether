# TETHER — Development Roadmap
## Document: 04_DEVELOPMENT_ROADMAP.md

---

> **For LLM Agents:** When a developer says "we're in Phase X, help me with Y", read this document to understand what has already been built, what the current phase's goals are, and what packages/patterns to use. Always refer to `03_ARCHITECTURE.md` for patterns and `06_DATABASE_SCHEMA.md` for data models.

---

## PHASE 0 — Environment Setup
**Goal:** Working dev environment, project scaffolded, dependencies installed

### 0.1 — Prerequisites
```bash
# Required on developer's machine:
# - Node.js 18+ (use nvm: nvm install 18)
# - Python 3.11+ (use pyenv recommended)
# - Git
# - VSCode with extensions: Python, ESLint, Prettier, Tailwind IntelliSense
# - SQLite browser (optional): DB Browser for SQLite

node --version   # should be 18+
python --version # should be 3.11+
git --version
```

### 0.2 — Project Structure Init
```bash
mkdir mnemo && cd mnemo
git init
echo "venv/\n.env\n__pycache__/\n*.pyc\nnode_modules/\ndist/" > .gitignore

# Backend scaffold
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
cd ..

# Frontend scaffold
npm create vite@latest frontend -- --template react
```

### 0.3 — Backend Dependencies

**`backend/requirements.txt`**
```
# Core
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-JWT-Extended==4.6.0
Flask-Bcrypt==1.0.1
Flask-CORS==4.0.1
Flask-Limiter==3.7.0

# Validation
marshmallow==3.21.3
flask-marshmallow==1.2.1
marshmallow-sqlalchemy==1.1.0

# Encryption
cryptography==42.0.8

# Utilities
python-dotenv==1.0.1
python-slugify==8.0.4

# Dev/Test
pytest==8.2.2
pytest-flask==1.3.0

# Production DB (install separately when ready for Turso):
# libsql-client==0.3.1
# sqlalchemy-libsql==0.1.1
```

```bash
pip install -r requirements.txt
```

### 0.4 — Frontend Dependencies

```bash
cd frontend

# Core
npm install react-router-dom@6 axios zustand

# Editor
npm install @tiptap/react @tiptap/pm @tiptap/starter-kit \
  @tiptap/extension-underline @tiptap/extension-image \
  @tiptap/extension-link @tiptap/extension-code-block-lowlight \
  @tiptap/extension-placeholder lowlight

# Styling
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Timeline Themes
npm install three          # Space theme
npm install gsap           # Camera animations (space theme)
npm install p5             # Canvas theme particles (optional)

# Calendar
# Option A: Build custom (recommended for full control)
# Option B: npm install react-big-calendar date-fns
# ⚠️ ASK DEVELOPER: Do you want to use react-big-calendar as a base or build custom?

# Utilities
npm install date-fns       # Date formatting
npm install react-window   # Virtual scrolling (canvas theme)
npm install react-spring   # Animations

# Dev
npm install -D @vitejs/plugin-react eslint prettier
```

### 0.5 — Environment Variables

**`backend/.env`** (never commit)
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=generate-a-random-string-here
JWT_SECRET_KEY=another-random-string-here
ENCRYPTION_KEY=generate-32-byte-hex-here
DATABASE_URL=sqlite:///mnemo_dev.db
FRONTEND_URL=http://localhost:5173
```

**Generate secrets:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"  # For SECRET_KEY and JWT_SECRET_KEY
python -c "import os; print(os.urandom(32).hex())"         # For ENCRYPTION_KEY
```

**`frontend/.env`**
```
VITE_API_URL=http://localhost:5000
```

### 0.6 — Verify Setup
```bash
# Backend
cd backend && source venv/bin/activate
flask run  # Should start on :5000

# Frontend (separate terminal)
cd frontend && npm run dev  # Should start on :5173

# Test: curl http://localhost:5000/api/health
# Should return: {"status": "ok"}
```

**Deliverable:** Both servers running, health endpoint returning 200.

---

## PHASE 1 — Backend Core
**Goal:** Auth system, Notes CRUD with encryption, Search, all tested

### 1.1 — Database Models
**Order of implementation:**
1. `User` model
2. `Note` model (with encryption hooks)
3. `NoteVersion` model
4. `Tag` and `NoteTag` association
5. Run `flask db init && flask db migrate -m "initial" && flask db upgrade`

→ See `06_DATABASE_SCHEMA.md` for complete model definitions

### 1.2 — Auth Endpoints
Implement `/api/auth/` blueprint:

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/register` | POST | No | Create user, hash password |
| `/login` | POST | No | Return access + refresh tokens |
| `/refresh` | POST | Refresh token | Return new access token |
| `/logout` | DELETE | Access token | Revoke refresh token (blocklist) |
| `/me` | GET | Access token | Return current user info |

### 1.3 — Notes CRUD Endpoints
Implement `/api/notes/` blueprint:

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | Yes | List user's notes (paginated) |
| `/` | POST | Yes | Create note (encrypt body) |
| `/:id` | GET | Yes | Get note (decrypt body) |
| `/:id` | PUT | Yes | Update note (re-encrypt body) |
| `/:id` | DELETE | Yes | Soft delete |
| `/:id/versions` | GET | Yes | Get revision history |
| `/:id/restore/:version_id` | POST | Yes | Restore a version |

### 1.4 — Search Endpoint
```
GET /api/search?q=query&tags=tag1,tag2&from=2024-01-01&to=2024-12-31
```
→ See `07_API_REFERENCE.md` for full spec

### 1.5 — Write Tests
```bash
pytest tests/ -v
# Minimum test coverage:
# - Register / Login / Refresh
# - Create note → read back → verify decryption
# - Search by title and body content
# - Soft delete + recovery
```

**Deliverable:** All auth and notes endpoints tested and passing.

---

## PHASE 2 — Frontend Core
**Goal:** Working editor, note list, global search overlay

### 2.1 — App Shell & Routing
```javascript
// App.jsx routes:
/ → Landing (if not auth'd) or redirect to /notes
/login → Login
/signup → Signup
/notes → NotesList (protected)
/notes/new → NoteEditorPage (protected)
/notes/:id → NoteEditorPage (protected)
/timeline → TimelinePage (protected)
/feed → FeedPage (protected)
/discover → DiscoverPage (protected)
/u/:username → ProfilePage (public)
/n/:slug → PublicNote (public)
/settings → SettingsPage (protected)
```

### 2.2 — Auth Flow
1. Login/Signup pages → call `/api/auth/login` or `/register`
2. Store tokens in Zustand (`authStore`) + persist refresh token in localStorage
3. Axios interceptor auto-attaches access token, auto-refreshes on 401
4. `ProtectedRoute` component checks auth state, redirects to `/login` if not authenticated

### 2.3 — Note Editor (TipTap)
Key implementation points:
- Separate title input (plain `<input>`) and TipTap editor for body
- Extensions: StarterKit, Underline, Link, Image, CodeBlock, Placeholder
- Auto-save hook: `useAutoSave(noteId, content, title)` — debounced 30s, fires on unmount
- Toolbar: Custom `Toolbar.jsx` using TipTap's `editor.chain().focus().*` commands
- Tag input: Pill-based input with Enter/comma to add, backspace to remove
- Visibility selector: Dropdown (Private/Unlisted/Public)

### 2.4 — Notes List
- Paginated list (`?page=1&per_page=20`)
- Filter by visibility and tags
- Sort: by `created_at desc` (default), `updated_at desc`, `title asc`
- Each card: title, excerpt (first 120 chars of body_plaintext), date, tags, visibility icon

### 2.5 — Global Search Overlay
- Opens on click of search bar or keyboard shortcut `Ctrl+K` / `Cmd+K`
- Traps focus, closes on Escape
- Calls `GET /api/search?q=` with 300ms debounce
- Shows title matches and body excerpt matches with highlight
- Arrow key navigation

**Deliverable:** User can sign up, create notes, edit them with auto-save, view list, and search.

---

## PHASE 3 — Timeline Themes
**Goal:** All 3 timeline themes working with drill-down

### 3.1 — Timeline Data
```
GET /api/notes/timeline?year=2024&month=12
```
Returns notes grouped for timeline rendering. See `07_API_REFERENCE.md`.

### 3.2 — Canvas Theme (build first — simplest)
- Virtual scrolling list (react-window or custom)
- CSS-based zoom with transform scale
- Date sticky headers
- White Canvas / Abyss toggle

### 3.3 — Calendar Theme
- Year → Month → Week → Day views
- Note dots on calendar days
- Side panel for note preview
- "Create note at this time" slot click

### 3.4 — Space Theme (most complex — last)
- Three.js scene setup (PerspectiveCamera, renderer, OrbitControls)
- Star field (THREE.Points)
- Timeline arm (CatmullRomCurve3 → TubeGeometry)
- Note spheres (SphereGeometry, instanced for performance)
- Camera fly-to animation (GSAP)
- HTML label overlay (CSS positioned via Vector3.project)
- Mobile fallback: CSS star field (no WebGL)

**Deliverable:** All 3 themes working, theme persists across sessions.

---

## PHASE 4 — Social Features
**Goal:** Public notes, following, feed, reactions, comments, discover

### 4.1 — Public Notes
- Note visibility field active
- Public note render route `/n/:slug` and `/u/:username/:slug`
- Clean blog view (no editor chrome)
- SEO meta tags (`<title>`, `og:title`, etc.)

### 4.2 — User Profiles
- Profile page at `/u/:username`
- Avatar upload (store as base64 or use Cloudinary in production — **ASK DEVELOPER**)
- Follow/unfollow button

### 4.3 — Social Graph
```
POST /api/social/follow/:user_id
DELETE /api/social/follow/:user_id
GET /api/social/feed
GET /api/social/followers
GET /api/social/following
```

### 4.4 — Reactions
```
POST /api/social/reactions  {note_id, emoji}
DELETE /api/social/reactions/:id
```

### 4.5 — Comments
```
GET /api/social/comments?note_id=X
POST /api/social/comments  {note_id, body, parent_id?}
DELETE /api/social/comments/:id
```

### 4.6 — Discover Page
- Trending notes (by reaction count in last 7 days)
- Recently active users
- Suggested users to follow

### 4.7 — Notifications (basic)
- In-app notification bell in top nav
- `GET /api/notifications` returns unread list
- Mark as read on click

**Deliverable:** Full social flow working locally.

---

## PHASE 5 — Production Migration
**Goal:** App running on Render with Turso database

### 5.1 — Turso Setup
```bash
# Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Login
turso auth login

# Create database
turso db create mnemo-prod

# Get connection URL
turso db show mnemo-prod --url

# Get auth token
turso db tokens create mnemo-prod
```

### 5.2 — Install Turso SQLAlchemy Driver
```bash
pip install libsql-client sqlalchemy-libsql
```

Update `requirements.txt` accordingly.

### 5.3 — Migrate Schema to Turso
```bash
# Set DATABASE_URL env to Turso URL
export DATABASE_URL="libsql+http://[org]-[db].turso.io?authToken=[token]"
flask db upgrade
```

### 5.4 — Render Deployment

**Backend (Flask):**
1. Create new Web Service on Render
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn run:app`
4. Add `gunicorn` to requirements.txt
5. Set all environment variables in Render dashboard

**Frontend (React/Vite):**
1. Create new Static Site on Render
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Set `VITE_API_URL` to your Flask service URL

**`render.yaml`** (optional, for infrastructure as code):
```yaml
services:
  - type: web
    name: mnemo-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: ENCRYPTION_KEY
        sync: false  # Set manually

  - type: web
    name: mnemo-frontend
    env: static
    buildCommand: npm run build
    staticPublishPath: ./dist
    envVars:
      - key: VITE_API_URL
        value: https://mnemo-backend.onrender.com
```

### 5.5 — CORS Configuration
```python
# In production, restrict CORS to your frontend domain
CORS(app, resources={
    r"/api/*": {
        "origins": os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    }
})
```

**Deliverable:** App live on Render, data in Turso.

---

## PHASE 6 — Polish & Launch
**Goal:** Bug fixes, performance, accessibility, launch readiness

### 6.1 — Performance
- [ ] Implement proper pagination on all list endpoints
- [ ] Add loading skeletons to all data-fetching views
- [ ] Three.js: Instance mesh for > 100 notes in Space theme
- [ ] React.lazy() + Suspense for Three.js (heavy bundle)
- [ ] Image optimization (lazy load in notes)

### 6.2 — Accessibility
- [ ] All interactive elements keyboard reachable
- [ ] ARIA labels on icon buttons
- [ ] Color contrast audit (WCAG 2.1 AA)
- [ ] Skip-to-content link

### 6.3 — Error Handling
- [ ] Global error boundary in React
- [ ] Toast notification system for API errors
- [ ] Offline detection banner

### 6.4 — Final QA Checklist
- [ ] Create account → write notes → search → find by content
- [ ] Make note public → share URL → view without login
- [ ] Follow a user → see their notes in feed
- [ ] Switch all 3 themes → timeline renders correctly
- [ ] Encryption: verify DB contains no plaintext note bodies
- [ ] Delete account flow
- [ ] Mobile: test on 375px viewport

---

## Package Summary (Full)

### Backend `requirements.txt` (complete)
```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-JWT-Extended==4.6.0
Flask-Bcrypt==1.0.1
Flask-CORS==4.0.1
Flask-Limiter==3.7.0
marshmallow==3.21.3
flask-marshmallow==1.2.1
marshmallow-sqlalchemy==1.1.0
cryptography==42.0.8
python-dotenv==1.0.1
python-slugify==8.0.4
pytest==8.2.2
pytest-flask==1.3.0
gunicorn==22.0.0
# Production only (uncomment when switching to Turso):
# libsql-client==0.3.1
# sqlalchemy-libsql==0.1.1
```

### Frontend `package.json` key deps
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.24.0",
    "axios": "^1.7.2",
    "zustand": "^4.5.4",
    "@tiptap/react": "^2.4.0",
    "@tiptap/pm": "^2.4.0",
    "@tiptap/starter-kit": "^2.4.0",
    "@tiptap/extension-underline": "^2.4.0",
    "@tiptap/extension-image": "^2.4.0",
    "@tiptap/extension-link": "^2.4.0",
    "@tiptap/extension-code-block-lowlight": "^2.4.0",
    "@tiptap/extension-placeholder": "^2.4.0",
    "lowlight": "^3.1.0",
    "three": "^0.166.0",
    "gsap": "^3.12.5",
    "p5": "^1.9.4",
    "date-fns": "^3.6.0",
    "react-window": "^1.8.10",
    "react-spring": "^9.7.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.3.3",
    "tailwindcss": "^3.4.6",
    "postcss": "^8.4.39",
    "autoprefixer": "^10.4.19",
    "eslint": "^9.7.0",
    "prettier": "^3.3.3"
  }
}
```

---

## Decision Log (Confirm with Developer)

| # | Decision | Options | Status |
|---|----------|---------|--------|
| 1 | Calendar theme base | Build custom vs. `react-big-calendar` | react-big-calendar |
| 2 | Avatar storage | Base64 in DB vs. Cloudinary vs. local disk | Base64 in DB |
| 3 | Email for password reset | SendGrid / Mailgun / skip for MVP | Skip for MVP |
| 4 | Mobile timeline fallback | CSS star field vs. simplified Three.js | simplified Three.js |
| 5 | Note export formats | Markdown only vs. add PDF (Phase 3+) | Markdown in phase 1, then add pdf option in phase 3 |
