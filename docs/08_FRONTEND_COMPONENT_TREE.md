# MNEMO — Frontend Component Tree & State Management
## Document: 08_FRONTEND_COMPONENT_TREE.md

---

## React Router Structure

```jsx
// App.jsx
<Router>
  <Routes>
    {/* Public */}
    <Route path="/" element={<Landing />} />
    <Route path="/login" element={<Login />} />
    <Route path="/signup" element={<Signup />} />
    <Route path="/n/:slug" element={<PublicNote />} />
    <Route path="/u/:username" element={<ProfilePage />} />

    {/* Protected (requires JWT) */}
    <Route element={<ProtectedRoute />}>
      <Route element={<AppShell />}>  {/* Sidebar + TopNav wrapper */}
        <Route path="/notes" element={<NotesList />} />
        <Route path="/notes/new" element={<NoteEditorPage />} />
        <Route path="/notes/:id" element={<NoteEditorPage />} />
        <Route path="/timeline" element={<TimelinePage />} />
        <Route path="/feed" element={<FeedPage />} />
        <Route path="/discover" element={<DiscoverPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Route>
  </Routes>
</Router>
```

---

## Component Hierarchy

```
App
├── ProtectedRoute
│   └── AppShell
│       ├── Sidebar
│       │   ├── NavLink (×5: Home, Feed, Notes, Discover, Profile)
│       │   ├── ThemeSwitcher
│       │   │   └── ThemeButton (×3: space, canvas, calendar)
│       │   └── SettingsLink
│       ├── TopNav
│       │   ├── SearchBar → SearchOverlay (portal)
│       │   ├── NewNoteButton
│       │   └── UserMenu
│       │       └── Avatar + Dropdown
│       └── <Outlet> (current page)
│
├── pages/
│   ├── Landing
│   │   ├── HeroSection (Three.js mini preview)
│   │   ├── FeatureHighlights
│   │   └── ThemePreviews
│   │
│   ├── Login / Signup
│   │   └── AuthForm
│   │
│   ├── NotesList
│   │   ├── NoteFilters (visibility, tags, sort)
│   │   └── NoteCard (×N)
│   │       ├── NoteTitle
│   │       ├── NoteExcerpt
│   │       ├── TagPills
│   │       └── VisibilityBadge
│   │
│   ├── NoteEditorPage
│   │   ├── EditorNav (back, share, menu)
│   │   ├── TitleInput
│   │   ├── Toolbar
│   │   │   └── ToolbarButton (×N)
│   │   ├── TipTapEditor
│   │   ├── StatusBar
│   │   │   ├── AutoSaveIndicator
│   │   │   ├── TagInput
│   │   │   ├── VisibilitySelector
│   │   │   └── WordCount
│   │   └── RevisionHistoryPanel (collapsible)
│   │
│   ├── TimelinePage
│   │   └── TimelineView (theme-aware router)
│   │       ├── SpaceTimeline (Three.js, lazy loaded)
│   │       ├── CanvasTimeline
│   │       │   ├── TimelineAxis
│   │       │   ├── DateMarker (×N)
│   │       │   └── NoteCard (×N, virtual)
│   │       └── CalendarTimeline
│   │           ├── CalendarHeader (nav, view selector)
│   │           ├── YearView → MonthMiniGrid (×12)
│   │           ├── MonthView → DayCell (×42)
│   │           ├── WeekView → TimeSlotGrid
│   │           ├── DayView → TimeSlotGrid
│   │           └── NotePreviewPanel (slide-in)
│   │
│   ├── FeedPage
│   │   └── FeedItem (×N)
│   │       ├── AuthorInfo
│   │       ├── NotePreview
│   │       └── ReactionBar
│   │
│   ├── DiscoverPage
│   │   ├── TrendingNotes
│   │   ├── SuggestedUsers
│   │   └── RecentPublicNotes
│   │
│   ├── ProfilePage
│   │   ├── ProfileHeader (avatar, bio, stats, follow button)
│   │   ├── ProfileTabs (Notes, Followers, Following)
│   │   └── PublicNoteGrid
│   │
│   ├── PublicNote
│   │   ├── BlogHeader (author, date)
│   │   ├── BlogContent (rendered HTML)
│   │   ├── ReactionBar
│   │   └── CommentThread
│   │       ├── CommentItem (×N)
│   │       │   └── CommentItem (replies, recursive)
│   │       └── CommentInput
│   │
│   └── SettingsPage
│       ├── AccountSection
│       ├── AppearanceSection
│       │   └── ThemePicker
│       ├── PrivacySection
│       └── DangerZone
│
└── SearchOverlay (React Portal, rendered in document.body)
    ├── SearchInput
    ├── RecentSearches
    ├── SearchResults
    │   └── SearchResultItem (×N)
    └── SearchFilters
```

---

## State Management

### Zustand Stores

#### `authStore.js`
```javascript
{
  user: null | { id, username, email, avatar_url, theme_pref },
  accessToken: null | string,
  refreshToken: null | string,  // persisted in localStorage
  
  // Actions
  setAuth(user, accessToken, refreshToken),
  updateUser(partialUser),
  clearAuth(),
  
  // Computed
  isAuthenticated: () => !!accessToken,
}
```

#### `notesStore.js`
```javascript
{
  notes: {},           // id → note object (cache)
  listIds: [],         // ordered IDs for current list view
  listMeta: null,      // { page, per_page, total }
  currentNoteId: null, // ID of note open in editor
  isSaving: false,
  lastSavedAt: null,
  
  // Actions
  setNotes(notes, meta),
  upsertNote(note),
  removeNote(id),
  setCurrentNote(id),
  setSaving(bool),
  setLastSaved(date),
}
```

#### `themeStore.js`
```javascript
{
  theme: 'canvas',  // 'space' | 'canvas' | 'calendar'
  canvasMode: 'white',  // 'white' | 'abyss' (Canvas theme sub-mode)
  
  // Actions
  setTheme(theme),
  setCanvasMode(mode),
}
```

#### `searchStore.js`
```javascript
{
  isOpen: false,
  query: '',
  results: [],
  isLoading: false,
  recentSearches: [],   // persisted
  
  // Actions
  openSearch(),
  closeSearch(),
  setQuery(q),
  setResults(results),
  addRecentSearch(q),
}
```

#### `uiStore.js`
```javascript
{
  sidebarCollapsed: false,
  notificationCount: 0,
  
  // Actions
  toggleSidebar(),
  setNotificationCount(n),
}
```

---

## Key Custom Hooks

### `useAutoSave(noteId, title, body)`
```javascript
// hooks/useAutoSave.js
import { useEffect, useCallback, useRef } from 'react'
import { useNotesStore } from '../store/notesStore'
import { updateNote } from '../api/notes'

export function useAutoSave(noteId, title, body) {
  const timerRef = useRef(null)
  const { setSaving, setLastSaved } = useNotesStore()

  const save = useCallback(async () => {
    if (!noteId) return
    setSaving(true)
    try {
      await updateNote(noteId, { title, body })
      setLastSaved(new Date())
    } finally {
      setSaving(false)
    }
  }, [noteId, title, body])

  useEffect(() => {
    timerRef.current = setTimeout(save, 30000)  // 30s debounce
    return () => clearTimeout(timerRef.current)
  }, [title, body, save])

  // Save on unmount
  useEffect(() => {
    return () => { save() }
  }, [save])

  return { save }  // expose for manual save (Ctrl+S)
}
```

### `useSearch()`
```javascript
// hooks/useSearch.js
import { useState, useEffect } from 'react'
import { searchNotes } from '../api/search'
import { useDebounce } from './useDebounce'

export function useSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const debouncedQuery = useDebounce(query, 300)

  useEffect(() => {
    if (!debouncedQuery.trim()) { setResults([]); return }
    setLoading(true)
    searchNotes(debouncedQuery)
      .then(({ data }) => setResults(data.data))
      .finally(() => setLoading(false))
  }, [debouncedQuery])

  return { query, setQuery, results, loading }
}
```

### `useTimeline(view, year, month)`
```javascript
// hooks/useTimeline.js
// Fetches timeline data from GET /api/notes/timeline
// Returns { data, loading, error }
// Manages drill-down state (view, year, month, day)
```

---

## TipTap Editor Setup

```jsx
// components/editor/NoteEditor.jsx
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import Placeholder from '@tiptap/extension-placeholder'
import { all, createLowlight } from 'lowlight'

const lowlight = createLowlight(all)

export function NoteEditor({ content, onChange }) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({ codeBlock: false }),
      Underline,
      Link.configure({ openOnClick: false }),
      Image,
      CodeBlockLowlight.configure({ lowlight }),
      Placeholder.configure({ placeholder: 'Start writing...' }),
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    editorProps: {
      attributes: {
        class: 'prose max-w-none focus:outline-none min-h-[400px]',
      },
    },
  })

  return <EditorContent editor={editor} />
}
```

---

## Three.js Space Timeline — Component Lifecycle

```jsx
// components/timeline/SpaceTimeline.jsx
import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

export default function SpaceTimeline({ notes }) {
  const mountRef = useRef(null)
  const sceneRef = useRef(null)

  useEffect(() => {
    // ─── SETUP ───
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(60, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000)
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    mountRef.current.appendChild(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true

    // Star field, timeline arm, note spheres setup...
    // (see 02_UI_WIREFRAMES_AND_THEMES.md Theme 1 for full spec)

    sceneRef.current = { scene, camera, renderer, controls }

    // ─── ANIMATION LOOP ───
    let animId
    const animate = () => {
      animId = requestAnimationFrame(animate)
      controls.update()
      renderer.render(scene, camera)
    }
    animate()

    // ─── CLEANUP (CRITICAL) ───
    return () => {
      cancelAnimationFrame(animId)
      controls.dispose()
      renderer.dispose()
      // Dispose all geometries and materials
      scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose()
        if (obj.material) {
          if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose())
          else obj.material.dispose()
        }
      })
      if (mountRef.current) {
        mountRef.current.removeChild(renderer.domElement)
      }
    }
  }, [notes])

  return <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />
}
```

**Lazy loading (critical for bundle size):**
```jsx
// pages/TimelinePage.jsx
const SpaceTimeline = React.lazy(() => import('../components/timeline/SpaceTimeline'))
// Wrap in <Suspense fallback={<LoadingSpinner />}> when rendering
```

---

## Tailwind Config

```javascript
// tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter Variable', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        // CSS variables consumed by themes
        // Actual values set in themes/*.css per active theme
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
```

**Install typography plugin:**
```bash
npm install -D @tailwindcss/typography
```
(Used for blog/public note view — `.prose` class)

---

## Vite Config

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],    // Separate chunk for Three.js
          tiptap: ['@tiptap/react', '@tiptap/starter-kit'],
        }
      }
    }
  }
})
```

---

## CSS Variables — Theme Application

```css
/* styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Applied dynamically via JS: document.documentElement.setAttribute('data-theme', theme) */

[data-theme="canvas"] {
  --bg-primary: #fafafa;
  --bg-secondary: #ffffff;
  --text-primary: #111827;
  --accent: #3b82f6;
  /* ... etc */
}

[data-theme="abyss"] {
  --bg-primary: #0a0a0a;
  --bg-secondary: #111111;
  --text-primary: #f9fafb;
  --accent: #60a5fa;
}

[data-theme="space"] {
  --bg-primary: #000008;
  --text-primary: #e0e7ff;
  --accent: #a78bfa;
}

[data-theme="calendar"] {
  --bg-primary: #ffffff;
  --text-primary: #1e293b;
  --accent: #3b82f6;
}
```

```javascript
// themeStore.js — apply to DOM
setTheme: (theme) => {
  set({ theme })
  document.documentElement.setAttribute('data-theme', theme)
}
```
