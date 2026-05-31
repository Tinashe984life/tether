# MNEMO — API Reference
## Document: 07_API_REFERENCE.md

---

> **Base URL:** `http://localhost:5000` (dev) | `https://mnemo-backend.onrender.com` (prod)
> **Auth:** Bearer JWT in `Authorization` header
> **Content-Type:** `application/json` on all requests with body

---

## AUTH — `/api/auth`

### POST `/api/auth/register`
Register a new user.

**Request:**
```json
{
  "username": "janedoe",
  "email": "jane@example.com",
  "password": "SecurePass123!"
}
```

**Response 201:**
```json
{
  "data": {
    "user": { "id": 1, "username": "janedoe", "email": "jane@example.com" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

**Errors:** 400 (validation), 409 (email/username taken)

---

### POST `/api/auth/login`
**Request:**
```json
{ "email": "jane@example.com", "password": "SecurePass123!" }
```

**Response 200:**
```json
{
  "data": {
    "user": { "id": 1, "username": "janedoe", "email": "jane@example.com", "theme_pref": "canvas" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

---

### POST `/api/auth/refresh`
**Auth:** Refresh token in header

**Response 200:**
```json
{ "data": { "access_token": "eyJ..." } }
```

---

### DELETE `/api/auth/logout`
**Auth:** Access token
Adds refresh token to blocklist.

**Response 200:**
```json
{ "message": "Logged out successfully" }
```

---

### GET `/api/auth/me`
**Auth:** Access token

**Response 200:**
```json
{
  "data": {
    "id": 1,
    "username": "janedoe",
    "email": "jane@example.com",
    "display_name": "Jane Doe",
    "bio": "...",
    "avatar_url": null,
    "theme_pref": "canvas",
    "default_visibility": "private",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

---

## NOTES — `/api/notes`

### GET `/api/notes`
List authenticated user's notes.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page (max 50) |
| `sort` | string | `created_at_desc` | `created_at_desc`, `created_at_asc`, `updated_at_desc`, `title_asc` |
| `visibility` | string | all | `private`, `unlisted`, `public` |
| `tags` | string | — | Comma-separated tag names |

**Response 200:**
```json
{
  "data": [
    {
      "id": 42,
      "title": "My Morning Thoughts",
      "slug": "my-morning-thoughts-a1b2c3",
      "visibility": "private",
      "word_count": 247,
      "created_at": "2024-12-14T08:30:00",
      "updated_at": "2024-12-14T09:00:00",
      "tags": ["journal", "morning"],
      "author": { "id": 1, "username": "janedoe", "avatar_url": null }
    }
  ],
  "meta": { "page": 1, "per_page": 20, "total": 143 }
}
```

---

### POST `/api/notes`
Create a new note.

**Request:**
```json
{
  "title": "My Morning Thoughts",
  "body": "<p>Today I woke up early...</p>",
  "visibility": "private",
  "tags": ["journal", "morning"]
}
```

**Response 201:**
```json
{
  "data": {
    "id": 42,
    "title": "My Morning Thoughts",
    "slug": "my-morning-thoughts-a1b2c3",
    "body": "<p>Today I woke up early...</p>",
    "visibility": "private",
    "word_count": 247,
    "created_at": "2024-12-14T08:30:00",
    "updated_at": "2024-12-14T08:30:00",
    "tags": ["journal", "morning"]
  }
}
```

---

### GET `/api/notes/:id`
Get a single note with body (decrypted). Only accessible by owner.

**Response 200:** Same as create response above.

**Errors:** 403 (not owner), 404 (not found)

---

### PUT `/api/notes/:id`
Update a note. Creates a version snapshot before saving.

**Request:** Same as POST (all fields optional)
```json
{
  "title": "Updated Title",
  "body": "<p>Updated content...</p>",
  "visibility": "public",
  "tags": ["updated", "tag"]
}
```

**Response 200:** Updated note object

---

### DELETE `/api/notes/:id`
Soft delete (sets `deleted_at`).

**Response 200:**
```json
{ "message": "Note deleted. You have 30 days to recover it." }
```

---

### GET `/api/notes/:id/versions`
List revision history.

**Response 200:**
```json
{
  "data": [
    { "id": 5, "version_number": 3, "title": "Draft title", "created_at": "..." },
    { "id": 4, "version_number": 2, "title": "Earlier draft", "created_at": "..." }
  ]
}
```

---

### GET `/api/notes/:id/versions/:version_id`
Get a specific version (includes decrypted body).

---

### POST `/api/notes/:id/restore/:version_id`
Restore a note to a previous version. Creates a new version of current state first.

---

### GET `/api/notes/timeline`
Get notes formatted for timeline rendering.

**Query params:**
| Param | Type | Description |
|-------|------|-------------|
| `view` | string | `year`, `month`, `week`, `day` |
| `year` | int | Required for month/week/day |
| `month` | int | Required for week/day |
| `week` | int | ISO week number, for week view |
| `day` | int | Day of month, for day view |

**Response 200 (year view):**
```json
{
  "data": {
    "view": "year",
    "year": 2024,
    "months": [
      { "month": 1, "note_count": 12, "labels": ["Jan"] },
      { "month": 2, "note_count": 8, "labels": ["Feb"] }
    ]
  }
}
```

**Response 200 (month view):**
```json
{
  "data": {
    "view": "month",
    "year": 2024,
    "month": 12,
    "days": [
      { "day": 14, "notes": [{ "id": 42, "title": "...", "created_at": "..." }] }
    ]
  }
}
```

---

## SEARCH — `/api/search`

### GET `/api/search`
Search user's notes by title and/or body content.

**Query params:**
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search query (required) |
| `tags` | string | Comma-separated tag filter |
| `from` | string | ISO date: `2024-01-01` |
| `to` | string | ISO date: `2024-12-31` |
| `page` | int | Page number |
| `per_page` | int | Default 20 |

**Response 200:**
```json
{
  "data": [
    {
      "id": 42,
      "title": "Project Alpha Notes",
      "slug": "project-alpha-notes-x1y2",
      "created_at": "2024-12-12T10:00:00",
      "tags": ["work"],
      "match_type": "body",
      "excerpt": "...key takeaways from the <mark>kickoff</mark> meeting..."
    }
  ],
  "meta": { "query": "kickoff", "total": 3, "page": 1, "per_page": 20 }
}
```

---

## USERS — `/api/users`

### GET `/api/users/:username`
Get public profile.

### PATCH `/api/users/me`
Update own profile (display_name, bio, avatar_url, theme_pref, default_visibility).

### GET `/api/users/me/tags`
Get all tags belonging to the current user.

---

## SOCIAL — `/api/social`

### POST `/api/social/follow/:user_id`
Follow a user.

**Response 201:** `{ "message": "Now following @username" }`

### DELETE `/api/social/follow/:user_id`
Unfollow.

### GET `/api/social/followers`
List followers of current user. Returns paginated user objects.

### GET `/api/social/following`
List users current user is following.

---

### GET `/api/social/feed`
Chronological feed of public notes from followed users.

**Query params:** `page`, `per_page`

**Response 200:**
```json
{
  "data": [
    {
      "id": 88,
      "title": "Why I journal every morning",
      "slug": "...",
      "visibility": "public",
      "excerpt": "First 200 chars of body...",
      "created_at": "2024-12-14T07:00:00",
      "tags": ["journal"],
      "author": { "id": 7, "username": "joebloggs", "avatar_url": "..." },
      "reaction_counts": { "👍": 4, "❤️": 12 },
      "comment_count": 3
    }
  ]
}
```

---

### POST `/api/social/reactions`
React to a note.

**Request:** `{ "note_id": 88, "emoji": "❤️" }`
**Response 201:** `{ "data": { "id": 9, "emoji": "❤️", "note_id": 88 } }`

### DELETE `/api/social/reactions/:id`
Remove a reaction.

---

### GET `/api/social/comments?note_id=88`
Get comments for a note (threaded).

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "body": "Great post!",
      "created_at": "...",
      "author": { "id": 3, "username": "someone", "avatar_url": null },
      "replies": [
        { "id": 2, "body": "Thanks!", "author": { ... }, "replies": [] }
      ]
    }
  ]
}
```

### POST `/api/social/comments`
**Request:** `{ "note_id": 88, "body": "Great post!", "parent_id": null }`

### DELETE `/api/social/comments/:id`
Soft delete own comment.

---

### GET `/api/social/discover`
Discover trending and new content.

**Response 200:**
```json
{
  "data": {
    "trending_notes": [ ...note objects... ],
    "suggested_users": [ ...user objects... ],
    "recent_public": [ ...note objects... ]
  }
}
```

---

## NOTIFICATIONS — `/api/notifications`

### GET `/api/notifications`
Get current user's notifications (unread first).

**Query params:** `unread_only=true`, `page`, `per_page`

**Response 200:**
```json
{
  "data": [
    {
      "id": 15,
      "type": "reaction",
      "is_read": false,
      "actor": { "username": "someone", "avatar_url": null },
      "note": { "id": 42, "title": "My note" },
      "created_at": "2024-12-14T12:00:00"
    }
  ],
  "meta": { "unread_count": 3 }
}
```

### PATCH `/api/notifications/:id/read`
Mark as read.

### PATCH `/api/notifications/read-all`
Mark all as read.

---

## PUBLIC — `/api/public` (No auth required)

### GET `/api/public/notes/:slug`
Get a public or unlisted note by slug (no auth needed).

**Response:** Full note object with body. Returns 404 if private or not found.

### GET `/api/public/users/:username`
Get public profile.

### GET `/api/public/users/:username/notes`
Get a user's public notes list.

---

## Health Check

### GET `/api/health`
```json
{ "status": "ok", "timestamp": "2024-12-14T12:00:00" }
```

---

## Error Codes Reference

| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION_ERROR` | 400 | Invalid input (see `details`) |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Valid auth but no permission |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `CONFLICT` | 409 | Duplicate (email, username, reaction) |
| `RATE_LIMITED` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal error |

## Rate Limits

| Endpoint Group | Limit |
|----------------|-------|
| `/api/auth/login` | 5/min per IP |
| `/api/auth/register` | 3/min per IP |
| `/api/notes` (write) | 60/min per user |
| `/api/search` | 30/min per user |
| All others | 120/min per user |
