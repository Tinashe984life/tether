# MNEMO — UI Wireframes & Theme Specifications
## Document: 02_UI_WIREFRAMES_AND_THEMES.md

---

> **How to read this document:** Each section describes a screen's layout in text wireframe form (boxes, labels, regions). Use these as implementation spec. The LLM agent should read these when building React components.

---

## SCREEN 1 — Landing / Marketing Page (`/`)

```
┌─────────────────────────────────────────────────────────────────┐
│  [MNEMO logo]                    [Login]  [Sign Up]             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│           H E R O   S E C T I O N                               │
│                                                                  │
│    [Animated preview of Space Theme timeline — three.js]         │
│                                                                  │
│    "Your notes. Across time. Never lost."                        │
│                                                                  │
│    [ Get Started Free ]   [ See how it works ]                  │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  FEATURE HIGHLIGHTS (3 columns)                                  │
│  [🔍 Search anything]  [🔐 Encrypted]  [🌌 Beautiful Timeline]  │
├─────────────────────────────────────────────────────────────────┤
│  THEME PREVIEWS (horizontal scroll cards)                        │
│  [Space Theme]  [Canvas Theme]  [Calendar Theme]                 │
├─────────────────────────────────────────────────────────────────┤
│  SOCIAL PROOF / FOOTER                                           │
└─────────────────────────────────────────────────────────────────┘
```

**Notes for implementation:**
- Hero background: Three.js particle/star field (static preview, not interactive on landing)
- CTA buttons: Primary (filled) + Secondary (outline)
- Theme cards: Short looping video or canvas animation of each theme

---

## SCREEN 2 — Auth Pages (`/login`, `/signup`)

```
┌─────────────────────────────────────────────────────────────────┐
│  [MNEMO logo]                                                    │
├──────────────────────────┬──────────────────────────────────────┤
│                          │                                       │
│   LEFT: Theme preview    │   RIGHT: Auth Form                   │
│   (animated mini-       │                                       │
│    timeline)             │   [ Email input          ]           │
│                          │   [ Password input       ]           │
│                          │   [ Confirm password *   ]  *signup  │
│                          │                                       │
│                          │   [ Log In / Sign Up ]               │
│                          │                                       │
│                          │   ── or ──                           │
│                          │   [Continue with Google] (Phase 3)   │
│                          │                                       │
│                          │   Already have account? Login        │
│                          │                                       │
└──────────────────────────┴──────────────────────────────────────┘
```

---

## SCREEN 3 — Main App Shell (authenticated)

```
┌──────────┬──────────────────────────────────────────────────────┐
│          │  TOP NAV                                              │
│ SIDEBAR  │  [🔍 Search bar (global)]  [+ New Note]  [Avatar ▾]  │
│          ├──────────────────────────────────────────────────────┤
│  [Home]  │                                                       │
│  [Feed]  │           MAIN CONTENT AREA                          │
│  [Notes] │         (changes by route / view)                    │
│  [Disco] │                                                       │
│  [Profi] │                                                       │
│  ──────  │                                                       │
│  [Theme] │                                                       │
│  [Sett.] │                                                       │
│          │                                                       │
└──────────┴──────────────────────────────────────────────────────┘
```

**Sidebar:**
- Collapsible to icon-only mode (< 768px: drawer/overlay)
- Active state highlights current route
- Theme switcher: Icon row of 3 theme glyphs (🌌 ⬜ 📅)
- Bottom: Settings gear icon

**Top Nav:**
- Global search bar: always visible, opens full search overlay on focus
- `+ New Note`: Creates blank note, navigates to editor
- Avatar dropdown: Profile, Settings, Logout

---

## SCREEN 4 — Note Editor (`/notes/new`, `/notes/:id/edit`)

```
┌──────────┬──────────────────────────────────────────────────────┐
│          │  EDITOR NAV BAR                                       │
│ SIDEBAR  │  [← Back]  [Title: "Untitled Note"]  [Share ▾] [···] │
│          ├──────────────────────────────────────────────────────┤
│          │  FORMATTING TOOLBAR (TipTap)                          │
│          │  [B][I][U][S][H1][H2][H3][—][•][1.][</>][🔗][🖼]    │
│          ├──────────────────────────────────────────────────────┤
│          │                                                       │
│          │   Click to add title...                               │
│          │                                                       │
│          │   Start writing...                                    │
│          │                                                       │
│          │                                                       │
│          │                                                       │
│          │                                                       │
│          ├──────────────────────────────────────────────────────┤
│          │  STATUS BAR:  [Auto-saved 2s ago]  [Tags: +tag]      │
│          │  [🔒 Private ▾]  [Word count: 247]  [Rev history]    │
└──────────┴──────────────────────────────────────────────────────┘
```

**Editor Details:**
- Title: Large H1 input at top, separate from body
- TipTap extensions needed: Bold, Italic, Underline, Strikethrough, Heading (1-3), HorizontalRule, BulletList, OrderedList, CodeBlock, Link, Image
- Auto-save: Debounced 30s, indicator in status bar
- Share dropdown: Private | Unlisted | Public
- Tags: Inline pill input with autocomplete (existing user tags)
- `···` Menu: Revision history, Delete, Export (markdown/PDF post-MVP)
- Right panel (collapsible): Note metadata — created date, word count, revision list

---

## SCREEN 5 — My Notes List (`/notes`)

```
┌──────────┬──────────────────────────────────────────────────────┐
│          │  My Notes          [Sort: Recent ▾]  [+ New Note]    │
│ SIDEBAR  ├──────────────────────────────────────────────────────┤
│          │  [ Filter: All | Private | Public | Unlisted ]        │
│          │  [ Tags: all-tags  #work  #journal  #ideas ... ]      │
│          ├──────────────────────────────────────────────────────┤
│          │  ┌────────────────────────────────────────────────┐  │
│          │  │ 📄 My Weekend Thoughts         Dec 14, 2024    │  │
│          │  │ "The morning light through the window..."       │  │
│          │  │ #journal  #personal             🔒 Private      │  │
│          │  └────────────────────────────────────────────────┘  │
│          │  ┌────────────────────────────────────────────────┐  │
│          │  │ 📄 Project Alpha Notes         Dec 12, 2024    │  │
│          │  │ "Key takeaways from the kickoff meeting..."     │  │
│          │  │ #work  #project                 🌐 Public      │  │
│          │  └────────────────────────────────────────────────┘  │
│          │  [ Load more... ]                                     │
└──────────┴──────────────────────────────────────────────────────┘
```

---

## SCREEN 6 — Global Search Overlay

```
┌─────────────────────────────────────────────────────────────────┐
│  ✕                                                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  🔍  Search your notes...                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  RECENT SEARCHES:  "project alpha"  "recipe ideas"  "monday"    │
│  ────────────────────────────────────────────────────────────   │
│  RESULTS (live, debounced):                                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 📄 Project Alpha Notes              Dec 12, 2024         │   │
│  │ "...key takeaways from the [kickoff] meeting..."          │   │
│  │  Match: body content                 #work               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 📄 Alpha release checklist          Nov 28, 2024         │   │
│  │ Title match                          #project            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  FILTER BY: [ Date range ] [ Tags ] [ Visibility ]              │
└─────────────────────────────────────────────────────────────────┘
```

**Notes:**
- Overlay covers full screen with backdrop blur
- Search input auto-focused on open
- Results categorized: Title matches first, then body excerpt matches
- Excerpt highlights the matched term in bold
- Keyboard navigation (↑↓ to move, Enter to open)

---

## SCREEN 7 — Timeline View (varies by theme — see Theme Specs below)

The timeline route is `/timeline`. The actual rendered view depends on active theme.

**Common behavior across all themes:**
- Clicking a note opens it in the editor (same tab, navigate back = return to timeline position)
- "Drill in": Click year → shows that year's months. Click month → shows that month's notes.
- "Drill out": Breadcrumb or back gesture
- Filtering: Tag filter chips float at top of timeline in all themes

---

## SCREEN 8 — Public Note / Blog View (`/n/:slug` or `/u/:username/:slug`)

```
┌─────────────────────────────────────────────────────────────────┐
│  [MNEMO logo]                [Login]  [Sign Up]   ← (not auth'd)│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [Author Avatar]  @username    Follow                          │
│   ─────────────────────────────────────────────────            │
│                                                                  │
│   # Note Title Here                                              │
│   Published: December 14, 2024                                  │
│                                                                  │
│   Note body rendered as clean HTML (no editor chrome)           │
│   Typographically optimized, max-width 680px centered           │
│                                                                  │
│   ─────────────────────────────────────────────────────────    │
│   [👍 12]  [❤️ 8]  [🔥 3]  [💡 5]          [Share]  [Copy link]│
│   ─────────────────────────────────────────────────────────    │
│                                                                  │
│   COMMENTS (23)                                                  │
│   ┌───────────────────────────────────────────────────────┐    │
│   │ @user2: "Great insight on..."        2 days ago        │    │
│   │   └ @author: "Thanks! I also think..."  1 day ago      │    │
│   └───────────────────────────────────────────────────────┘    │
│   [ Write a comment... ] (requires login)                       │
│                                                                  │
│   MORE FROM @username:                                           │
│   [Note card] [Note card] [Note card]                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## SCREEN 9 — Social Feed (`/feed`)

```
┌──────────┬──────────────────────────────────────────────────────┐
│          │  Your Feed                  [Discover]               │
│ SIDEBAR  ├──────────────────────────────────────────────────────┤
│          │  ┌────────────────────────────────────────────────┐  │
│          │  │ [Avatar] @jane_writes · 3h ago                  │  │
│          │  │ ## Why I journal every morning                  │  │
│          │  │ "The practice started in 2019 when I..."        │  │
│          │  │ [Read more →]                                   │  │
│          │  │ [👍 4] [❤️ 12] [💬 3]    [Follow]             │  │
│          │  └────────────────────────────────────────────────┘  │
│          │  [Load more]                                          │
└──────────┴──────────────────────────────────────────────────────┘
```

---

## SCREEN 10 — User Profile (`/u/:username`)

```
┌─────────────────────────────────────────────────────────────────┐
│  [Cover / Banner area — optional, user uploadable]               │
│  [Avatar]  @username                                             │
│  Bio text here                                                   │
│  [X notes]  [Y followers]  [Z following]   [Follow / Edit]      │
├─────────────────────────────────────────────────────────────────┤
│  [ Notes ] [ Following ] [ Followers ]                           │
│  ─────────────────────────────────────────────────────────────  │
│  [Note card grid — public notes only for other users]            │
└─────────────────────────────────────────────────────────────────┘
```

---

## SCREEN 11 — Settings (`/settings`)

```
┌──────────┬──────────────────────────────────────────────────────┐
│          │  Settings                                             │
│ SIDEBAR  ├──────────────────────────────────────────────────────┤
│          │  ACCOUNT                                              │
│          │  Email: user@example.com         [Change]            │
│          │  Password:  ••••••••             [Change]            │
│          │  Username:  @myusername          [Change]            │
│          │                                                       │
│          │  APPEARANCE                                           │
│          │  Theme:  [🌌 Space] [⬜ Canvas] [📅 Calendar]        │
│          │  (Clicking theme tile = instant preview + save)       │
│          │                                                       │
│          │  PRIVACY & SECURITY                                   │
│          │  Default note visibility: [Private ▾]                 │
│          │  Export all my data: [Download ZIP]                   │
│          │  Delete account: [Delete — requires confirm]          │
│          │                                                       │
│          │  NOTIFICATIONS (Post-MVP)                             │
│          │  [ ] New follower                                     │
│          │  [ ] Reaction on my notes                            │
│          │  [ ] Comment on my notes                             │
└──────────┴──────────────────────────────────────────────────────┘
```

---

---

# THEME SPECIFICATIONS

---

## THEME 1 — SPACE (Galactic Timeline)

**Library:** Three.js (primary) with post-processing (bloom effect)
**Aesthetic:** Dark space, stars, nebulae, notes as celestial objects on a galactic arm timeline

### Visual Concept
- Background: Deep space — black with procedurally generated star field (Three.js `Points` geometry)
- Nebula clouds: Semi-transparent colored blobs (GLSL shader or layered sprites)
- Timeline: A curved "galactic arm" — a glowing arc/spiral line running through the scene
- Notes: Represented as **planets/stars** on or near the timeline arm. Size = note word count. Color = tag color-code
- Zoom levels:
  - **Galaxy view** (zoomed out): See years as constellations/clusters
  - **Constellation view** (mid): See months as star clusters within a year
  - **Star view** (close): See individual note-stars for a month
  - **Planet view** (closest): Click a star → expands to planet with note preview card

### Controls
- **Scroll wheel / pinch**: Zoom in/out along the timeline arm
- **Click + drag**: Orbit / pan the camera
- **Click a note-star**: Camera flies to it (Three.js tween animation), shows note preview panel
- **Double-click / "Open"**: Opens note in editor

### Technical Approach
```
- Three.js scene with OrbitControls (limited axes to prevent disorientation)
- Stars: THREE.Points with custom ShaderMaterial for twinkling
- Timeline arm: THREE.CatmullRomCurve3 rendered as TubeGeometry with bloom
- Note markers: THREE.SphereGeometry (size proportional to word count)
- Camera transitions: GSAP or custom lerp animation
- Label overlay: HTML div elements positioned via THREE.Vector3.project() for note titles
- Performance: Instanced mesh for stars (>1000 points), LOD for note spheres
```

### Color Palette
```css
--space-bg: #000008;
--space-star: #ffffff;
--space-nebula-1: #1a0533;
--space-nebula-2: #0d1b4a;
--space-timeline-arm: #4fc3f7;
--space-note-glow: #a78bfa;
--space-text: #e0e7ff;
--space-accent: #f59e0b;
```

---

## THEME 2 — CANVAS (White/Abyss Infinite Scroll)

**Library:** Custom CSS + React Spring / Framer Motion + optional p5.js for subtle particle field
**Aesthetic:** The "infinite canvas" — a clean, infinite vertical/horizontal timeline of floating note cards

### Visual Concept
- Background: Two sub-modes the user can toggle:
  - **White Canvas**: Pure white background, soft drop shadows on note cards — like paper on a light table
  - **Abyss**: Pure black/near-black background, note cards glow with a subtle white border — like constellations of thought in darkness
- Timeline: A thin vertical or horizontal line (user preference) with notes arranged as cards hanging off it
- Cards: Minimal, rectangular. Show note title, first ~2 lines, date, tags
- Spacing: Time gaps between notes = proportional spacing on the axis (sparse periods = more space)
- Zoom: Cards can be scaled (CSS transform scale) — zoomed out = more cards visible, smaller; zoomed in = fewer cards, more detail visible

### Controls
- **Scroll**: Move along timeline (vertical default)
- **Ctrl+Scroll / pinch**: Zoom in/out (scale CSS transform on container)
- **Click card**: Expand to full preview in-place (card grows, shows more content)
- **Double-click / "Open"**: Navigates to editor

### Technical Approach
```
- Virtual scrolling for performance (react-window or custom)
- Timeline line: SVG or CSS pseudo-element
- Card expansion: CSS transition + React state
- Date markers: Sticky headers as you scroll (year, month)
- Optional p5.js background: Subtle floating dots/particles in Abyss mode only
```

### Color Palette (White Canvas)
```css
--canvas-bg: #fafafa;
--canvas-line: #e5e7eb;
--canvas-card-bg: #ffffff;
--canvas-card-border: #e5e7eb;
--canvas-card-shadow: rgba(0,0,0,0.08);
--canvas-text-primary: #111827;
--canvas-text-secondary: #6b7280;
--canvas-accent: #3b82f6;
```

### Color Palette (Abyss)
```css
--abyss-bg: #0a0a0a;
--abyss-line: #1f2937;
--abyss-card-bg: #111111;
--abyss-card-border: #374151;
--abyss-card-glow: rgba(255,255,255,0.03);
--abyss-text-primary: #f9fafb;
--abyss-text-secondary: #9ca3af;
--abyss-accent: #60a5fa;
```

---

## THEME 3 — CALENDAR (Standard + Drill-Down)

**Library:** Custom React calendar component (or `react-big-calendar` as base, heavily customized)
**Aesthetic:** Clean, structured calendar UI — familiar Google Calendar / macOS Calendar feel but branded

### Visual Concept
- Standard calendar grid with drill-down capability:
  - **Year View**: 12 month mini-grids. Days with notes are marked with colored dots. Click month → Month view.
  - **Month View**: Full month grid. Days with notes show count badge. Click day → Day view.
  - **Week View**: 7-column grid with hourly rows. Notes shown as event blocks (time = created_at time).
  - **Day View**: Hourly timeline for one day. Notes shown in order of creation time as blocks.
- Each note block shows: icon, title (truncated), first line of content
- Click any note block → Side panel slides in with full note preview
- "New note" by clicking any empty time slot (pre-fills created_at to that date/time)

### Controls
- **← →** arrows: Navigate previous/next (month/week/day)
- **[Today]** button: Jump to current date
- **View selector**: [Year] [Month] [Week] [Day] button group
- **Click note block**: Open preview panel
- **Click empty slot**: Create new note at that time

### Technical Approach
```
- React component: CalendarView with viewMode state (year|month|week|day)
- Year view: Grid of 12 MiniMonth components
- Month view: Standard 6x7 grid
- Week/Day view: CSS grid with time slots as rows
- Note blocks: Positioned with CSS (top = time offset, height = duration/fixed)
- Side panel: Slide-in drawer showing note content
```

### Color Palette
```css
--cal-bg: #ffffff;
--cal-header-bg: #f8fafc;
--cal-grid-line: #e2e8f0;
--cal-today: #dbeafe;
--cal-note-block: #3b82f6;
--cal-note-block-text: #ffffff;
--cal-note-dot: #6366f1;
--cal-weekend: #f8fafc;
--cal-text: #1e293b;
--cal-text-muted: #94a3b8;
```

---

## Theme Switching Implementation Notes

```javascript
// Theme stored in user profile (DB) + localStorage fallback
const THEMES = ['space', 'canvas', 'calendar'];

// Context provider
const ThemeContext = React.createContext('canvas'); // default

// On app load: read from localStorage, then sync with user profile from API
// On switch: update localStorage immediately (instant), then PATCH /api/users/me/preferences
```

- Theme switch should be **instant** (no page reload)
- Timeline component renders the correct theme component based on context
- Three.js scene should unmount when switching away from Space theme (cleanup WebGL context)

---

## Responsive Breakpoints

```
Mobile:   < 640px  — Sidebar becomes bottom nav bar; editor is full screen; Space theme simplified (no Three.js, use CSS star field)
Tablet:   640-1024px — Sidebar collapsible icon mode; timeline single column
Desktop:  > 1024px — Full layout as described above
```
