# MNEMO — Product Requirements Document (PRD)
## Document: 01_PRODUCT_REQUIREMENTS.md

---

## 1. Problem Statement

Users accumulate notes across random local folders, apps, and devices. They forget filenames, forget what a note contained, and have no way to visually browse their note history. There is no single tool that combines a distraction-free writing experience, powerful full-text search, beautiful chronological visualization, secure encryption, and social sharing in one place.

---

## 2. Vision

MNEMO is a web-based notepad, diary, and word editor that:
- Replaces scattered local files with a single, searchable, encrypted cloud store
- Lets users *see* their notes across time through multiple visual paradigms (space, canvas, calendar)
- Enables selective sharing — from private diary entries to public blog posts
- Builds light social network effects through follows, reactions, and discovery

---

## 3. Users & Personas

| Persona | Needs |
|---------|-------|
| **The Journaller** | Daily diary entries, private, chronological browsing, mobile-friendly |
| **The Knowledge Worker** | Fast search, rich text formatting, linking notes, export |
| **The Creator/Blogger** | Public sharing, blog-format view, audience feedback |
| **The Visual Thinker** | Timeline/calendar view, theme customization, spatial navigation |

---

## 4. Core Features

### 4.1 Note Management
- Create, read, update, delete (CRUD) notes
- Rich text editor (bold, italic, headings, lists, code blocks, links, images)
- Auto-save every 30 seconds and on blur
- Notes are stored with: title, body, created_at, updated_at, tags, visibility, user_id
- Untitled notes auto-titled: "Note — [Date] [Time]"
- Tag support (user-defined, multi-tag)
- Note versioning / revision history (MVP: last 10 versions)

### 4.2 Search
- Search by **title** (partial match, case-insensitive)
- Search by **body content** — full-text search (FTS5 in SQLite, Turso FTS in prod)
- Search by **tags**
- Search by **date range**
- Search results ranked by relevance + recency
- Live search (debounced, 300ms)
- Highlight matching excerpts in results

### 4.3 Chronological Timeline / Views
All notes are stored with timestamps and displayed in chronological order. Three view themes (see `02_UI_WIREFRAMES_AND_THEMES.md` for visuals):

1. **Space Theme** — Galactic scrollable timeline, notes as stars/planets, zoom in/out with scroll wheel (Three.js)
2. **Canvas Theme** — Clean infinite scroll timeline, minimal white/dark abyss, notes as floating cards
3. **Calendar Theme** — Standard calendar grid (Year → Month → Week → Day drill-down)

User can switch themes from settings. Theme persists in user profile.

### 4.4 Encryption
- All note body content encrypted **at rest** using AES-256-GCM
- Encryption key derived per-user (server-side), stored hashed
- In-transit: HTTPS only (Render provides TLS)
- MVP: server-side encryption. Future: optional client-side E2E encryption
- Public/shared notes are decrypted for rendering; private notes never transmitted in plaintext without auth

### 4.5 Sharing & Blog Format
- Each note has a `visibility` field: `private` | `unlisted` | `public`
- Public notes get a unique shareable URL: `/n/[note_slug]` or `/u/[username]/[note_slug]`
- Public notes render in a clean blog/reader format (no editor chrome)
- Unlisted = accessible via direct link but not indexed/discoverable
- Private = only visible to owner

### 4.6 Social Features (Network Effects)
- User profiles with username, avatar, bio
- Follow / Unfollow other users
- **Feed**: Chronological feed of public notes from followed users
- **Reactions**: Emoji reactions on public notes (👍❤️🔥💡)
- **Comments** on public notes (threaded, one level deep)
- **Discover page**: Trending public notes, recently active users
- **Notifications**: New follower, reaction on your note, comment on your note

---

## 5. User Stories

### Authentication
- As a user, I can sign up with email + password
- As a user, I can log in and receive a JWT access token
- As a user, I can refresh my session without re-logging in
- As a user, I can reset my password via email (Phase 2+)

### Notes
- As a user, I can create a new note and it auto-saves as I type
- As a user, I can search my notes by title or content and find results instantly
- As a user, I can browse all my notes in a chronological timeline
- As a user, I can tag notes and filter by tag
- As a user, I can view previous versions of a note
- As a user, I can delete a note (soft delete with 30-day recovery)

### Timeline / Views
- As a user, I can switch between Space, Canvas, and Calendar views
- As a user, I can zoom in from year view to a single note in all themes
- As a user, I can click any note in the timeline to open it in the editor

### Sharing
- As a user, I can make a note public and share its URL
- As a user, I can view a public note without being logged in
- As a user, I can make a note unlisted (link-only)

### Social
- As a user, I can follow another user and see their public notes in my feed
- As a user, I can react to a public note
- As a user, I can comment on a public note
- As a user, I can discover trending and new notes on a discovery page

### Customization
- As a user, I can choose between 3 visual themes
- As a user, my theme preference persists across sessions

---

## 6. Non-Functional Requirements

| Category | Requirement |
|----------|------------|
| Performance | Search results < 200ms; Editor auto-save < 50ms latency |
| Security | All notes encrypted at rest; JWT expiry 15min access / 7day refresh |
| Scalability | Turso handles horizontal read scaling; write queue for high volume |
| Accessibility | WCAG 2.1 AA — keyboard navigable, ARIA labels, sufficient contrast |
| Browser Support | Chrome 110+, Firefox 110+, Safari 16+, Edge 110+ |
| Mobile | Responsive down to 375px; touch-friendly timeline gestures |
| Offline (Post-MVP) | Service worker for offline editing with sync queue |

---

## 7. Out of Scope for MVP

- Mobile native app
- Real-time collaborative editing
- AI summarization / generation within notes
- Import from other apps (Notion, Evernote, etc.) — Phase 3+
- Client-side E2E encryption — Phase 3+
- Email verification — Phase 2
- OAuth (Google/GitHub login) — Phase 3+

---

## 8. Success Metrics

- User can create a note and find it by content search in < 30 seconds
- Notes persist correctly across sessions with encryption intact
- Timeline renders > 100 notes without frame drops
- Public note URL accessible without login in < 1s
