# MNEMO — System Architecture
## Document: 03_ARCHITECTURE.md

---

## 1. High-Level Architecture

```
                        ┌─────────────────────────────┐
                        │     Browser (React + Vite)   │
                        │  - TipTap editor             │
                        │  - Three.js / p5.js timeline │
                        │  - React Router v6           │
                        │  - Zustand state store       │
                        └──────────────┬──────────────┘
                                       │ HTTPS / JSON REST API
                        ┌──────────────▼──────────────┐
                        │     Flask Backend            │
                        │  - JWT authentication        │
                        │  - REST API blueprints       │
                        │  - AES-256-GCM encryption    │
                        │  - SQLAlchemy ORM            │
                        └──────────────┬──────────────┘
                                       │
                        ┌──────────────▼──────────────┐
                        │     Database                 │
                        │  LOCAL:  SQLite + FTS5       │
                        │  PROD:   Turso (LibSQL)      │
                        └─────────────────────────────┘
```

---

## 2. Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── config.py            # Config classes (Dev, Prod)
│   ├── extensions.py        # db, jwt, migrate instances
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── note.py
│   │   ├── note_version.py
│   │   ├── tag.py
│   │   ├── follow.py
│   │   ├── reaction.py
│   │   ├── comment.py
│   │   └── notification.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # /api/auth/*
│   │   ├── notes.py         # /api/notes/*
│   │   ├── search.py        # /api/search
│   │   ├── social.py        # /api/follow, /api/feed, /api/reactions
│   │   ├── users.py         # /api/users/*
│   │   └── public.py        # /api/public/* (unauthenticated)
│   └── utils/
│       ├── encryption.py    # AES-256-GCM helpers
│       ├── slugify.py       # Note slug generation
│       └── search.py        # FTS helpers
├── migrations/              # Flask-Migrate files
├── tests/
│   ├── test_auth.py
│   ├── test_notes.py
│   └── test_search.py
├── .env                     # Never commit — see .env.example
├── .env.example
├── requirements.txt
└── run.py                   # Entry point: flask run
```

### App Factory Pattern

```python
# app/__init__.py
from flask import Flask
from .extensions import db, jwt, migrate
from .api import auth_bp, notes_bp, search_bp, social_bp, users_bp, public_bp

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(public_bp, url_prefix='/api/public')
    
    return app
```

### Config Pattern

```python
# app/config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')  # 32-byte hex string
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mnemo_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    # Turso/LibSQL connection:
    # SQLALCHEMY_DATABASE_URI set via env: libsql+http://[org]-[db].turso.io
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
```

---

## 3. Frontend Architecture

### Directory Structure

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── main.jsx             # React entry point
│   ├── App.jsx              # Router setup
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── TopNav.jsx
│   │   │   └── AppShell.jsx
│   │   ├── editor/
│   │   │   ├── NoteEditor.jsx
│   │   │   ├── Toolbar.jsx
│   │   │   └── TagInput.jsx
│   │   ├── timeline/
│   │   │   ├── TimelineView.jsx    # Router: picks theme component
│   │   │   ├── SpaceTimeline.jsx   # Three.js
│   │   │   ├── CanvasTimeline.jsx  # Infinite scroll
│   │   │   └── CalendarTimeline.jsx
│   │   ├── search/
│   │   │   └── SearchOverlay.jsx
│   │   ├── social/
│   │   │   ├── Feed.jsx
│   │   │   ├── NoteCard.jsx
│   │   │   ├── ReactionBar.jsx
│   │   │   └── CommentThread.jsx
│   │   ├── public/
│   │   │   └── BlogView.jsx
│   │   └── ui/              # Reusable primitives
│   │       ├── Button.jsx
│   │       ├── Modal.jsx
│   │       ├── Drawer.jsx
│   │       └── Avatar.jsx
│   ├── pages/
│   │   ├── Landing.jsx
│   │   ├── Login.jsx
│   │   ├── Signup.jsx
│   │   ├── Home.jsx
│   │   ├── NotesList.jsx
│   │   ├── NoteEditorPage.jsx
│   │   ├── TimelinePage.jsx
│   │   ├── FeedPage.jsx
│   │   ├── DiscoverPage.jsx
│   │   ├── ProfilePage.jsx
│   │   ├── PublicNote.jsx
│   │   └── SettingsPage.jsx
│   ├── store/
│   │   ├── authStore.js     # Zustand: user, tokens
│   │   ├── notesStore.js    # Zustand: notes cache
│   │   └── themeStore.js    # Zustand: active theme
│   ├── hooks/
│   │   ├── useNotes.js
│   │   ├── useSearch.js
│   │   └── useAutoSave.js
│   ├── api/
│   │   └── client.js        # Axios instance with interceptors
│   ├── utils/
│   │   └── dates.js
│   └── styles/
│       ├── globals.css      # Tailwind base + CSS vars
│       └── themes/
│           ├── space.css
│           ├── canvas.css
│           └── calendar.css
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

### State Management (Zustand)

```javascript
// store/authStore.js
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(persist(
  (set) => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    setAuth: (user, accessToken, refreshToken) => set({ user, accessToken, refreshToken }),
    clearAuth: () => set({ user: null, accessToken: null, refreshToken: null }),
  }),
  { name: 'mnemo-auth', partialize: (s) => ({ refreshToken: s.refreshToken, user: s.user }) }
))

// store/themeStore.js
export const useThemeStore = create(persist(
  (set) => ({
    theme: 'canvas', // 'space' | 'canvas' | 'calendar'
    setTheme: (theme) => set({ theme }),
  }),
  { name: 'mnemo-theme' }
))
```

### API Client (Axios + JWT Interceptor)

```javascript
// api/client.js
import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
})

// Attach access token to every request
client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
client.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          })
          useAuthStore.getState().setAuth(
            useAuthStore.getState().user,
            data.access_token,
            refreshToken
          )
          error.config.headers.Authorization = `Bearer ${data.access_token}`
          return client(error.config)
        } catch {
          useAuthStore.getState().clearAuth()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default client
```

---

## 4. Encryption Architecture

### Strategy: Server-Side AES-256-GCM

All note body content is encrypted before writing to DB and decrypted after reading from DB. The user never sees this happening — it's transparent.

```
[User types in editor]
        ↓
[Frontend sends plaintext body via HTTPS]
        ↓
[Flask receives, encrypts with AES-256-GCM]
        ↓
[Stores: encrypted_body (base64), nonce (base64), tag (base64)]
        ↓
[On read: Flask decrypts, sends plaintext back via HTTPS]
```

### Encryption Key Strategy

**MVP (simplest safe approach):**
- One master encryption key stored in environment variable (`ENCRYPTION_KEY`)
- Key is a 32-byte random hex string, generated once at setup
- All notes encrypted with this key

**Future (per-user keys):**
- Each user has a unique derived key: `HKDF(master_key, user_id)`
- If a user's account is deleted, their key can be independently revoked

### Implementation

```python
# app/utils/encryption.py
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_key() -> bytes:
    key_hex = os.environ.get('ENCRYPTION_KEY')
    if not key_hex:
        raise ValueError("ENCRYPTION_KEY not set")
    return bytes.fromhex(key_hex)

def encrypt(plaintext: str) -> dict:
    """Returns dict with nonce and ciphertext, both base64-encoded."""
    key = get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return {
        'nonce': base64.b64encode(nonce).decode(),
        'ciphertext': base64.b64encode(ciphertext).decode(),
    }

def decrypt(nonce_b64: str, ciphertext_b64: str) -> str:
    """Returns decrypted plaintext string."""
    key = get_key()
    aesgcm = AESGCM(key)
    nonce = base64.b64decode(nonce_b64)
    ciphertext = base64.b64decode(ciphertext_b64)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')

# Key generation (run once, store result in .env):
# python -c "import os; print(os.urandom(32).hex())"
```

---

## 5. Search Architecture

### SQLite FTS5 (Local Development)

```sql
-- FTS virtual table mirrors notes table
CREATE VIRTUAL TABLE notes_fts USING fts5(
    title,
    body_plaintext,  -- decrypted body stored for search only
    content='notes',
    content_rowid='id'
);

-- Trigger to keep FTS in sync
CREATE TRIGGER notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, body_plaintext)
    VALUES (new.id, new.title, new.body_plaintext);
END;
-- Similar triggers for UPDATE and DELETE
```

**Note on search + encryption:** We store a separate `body_plaintext` column (or the FTS table) containing the decrypted text purely for search indexing. This means the DB has both encrypted body (for storage) and plaintext (for search). This is a pragmatic MVP trade-off.

**Production security note:** Turso (LibSQL) FTS is similarly indexed. For higher security (search on encrypted data), a future phase could implement a bloom filter index or use a search-specific encrypted index approach.

### Search Query

```python
# app/utils/search.py
from app.extensions import db
from sqlalchemy import text

def search_notes(query: str, user_id: int, limit: int = 20):
    sql = text("""
        SELECT n.id, n.title, n.created_at, n.updated_at,
               snippet(notes_fts, 1, '<mark>', '</mark>', '...', 20) as excerpt,
               bm25(notes_fts) as rank
        FROM notes_fts
        JOIN notes n ON n.id = notes_fts.rowid
        WHERE notes_fts MATCH :query
          AND n.user_id = :user_id
          AND n.deleted_at IS NULL
        ORDER BY rank
        LIMIT :limit
    """)
    return db.session.execute(sql, {'query': query, 'user_id': user_id, 'limit': limit}).fetchall()
```

---

## 6. Local → Production Migration Plan (Turso)

| Step | Action |
|------|--------|
| 1 | Build and test entirely on SQLite locally |
| 2 | Set `DATABASE_URL` env var to Turso LibSQL connection string |
| 3 | Run `flask db upgrade` against Turso (Flask-Migrate works with LibSQL via `sqlalchemy-libsql`) |
| 4 | Migrate existing local SQLite data using Turso's migration tool or custom script |
| 5 | Update `SQLALCHEMY_DATABASE_URI` in production config |
| 6 | Verify FTS5 compatibility — Turso supports FTS5, same syntax |

**Required packages for Turso:**
```
libsql-client
sqlalchemy-libsql  # Adds libsql+http:// dialect to SQLAlchemy
```

**Connection string format:**
```
libsql+http://[your-org]-[your-db].turso.io?authToken=[your-token]
```

---

## 7. Security Checklist

- [ ] HTTPS enforced in production (Render handles this)
- [ ] JWT secret is a strong random string (not default)
- [ ] `ENCRYPTION_KEY` set in Render environment variables (never in code)
- [ ] Password hashing: bcrypt via `flask-bcrypt` (work factor 12+)
- [ ] CORS: Flask-CORS configured to allow only frontend domain in production
- [ ] Rate limiting: `flask-limiter` on auth endpoints (5 attempts/min)
- [ ] SQL injection: SQLAlchemy ORM prevents raw string interpolation
- [ ] Input validation: `marshmallow` schemas on all API inputs
- [ ] Sensitive routes require `@jwt_required()`
- [ ] Soft delete: `deleted_at` timestamp, not hard delete
