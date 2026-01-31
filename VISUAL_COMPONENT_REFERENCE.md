# 🎨 NIS SuperApp Dashboard - Visual Component Reference

## Dashboard Layout Map

```
┌────────────────────────────────────────────────────────────────┐
│                        TOP NAVIGATION                          │
│  [Logo] [Spacer]                [Theme] [🔔] [Avatar]         │
└────────────────────────────────────────────────────────────────┘

                        HEADER SECTION
                    "Welcome back, [Name]! 👋"

┌──────────────────┬─────────────────────────────────────────────┐
│                  │                                             │
│  PROFILE CARD    │  ╔═══════════════════════════════════════╗ │
│  ┌─────────────┐ │  ║ 🌟 WEEKLY STARS (Hall of Fame)        ║ │
│  │   Avatar    │ │  ╠═══════════════════════════════════════╣ │
│  │   [name]    │ │  ║ [S1] [S2] [S3] [S4] [S5]            ║ │
│  │   [class]   │ │  ║ +100 +95  +90  +85  +80   XP         ║ │
│  ├─────────────┤ │  ╚═══════════════════════════════════════╝ │
│  │ Shanyraq    │ │                                             │
│  │ [Team Name] │ │  ╔═══════════════════════════════════════╗ │
│  ├─────────────┤ │  ║ 📅 UPCOMING EVENTS (Carousel)        ║ │
│  │  Rank: [⭐] │ │  ╠═══════════════════════════════════════╣ │
│  │            │ │  ║ [E1] [E2] [E3]  ...                 ║ │
│  ├─────────────┤ │  ║ Assembly | Quiz Night | Sports Day   ║ │
│  │ Season: 350 │ │  ║ Next Wed  Tomorrow    in 3 days     ║ │
│  │ Total: 2850 │ │  ╚═══════════════════════════════════════╝ │
│  ├─────────────┤ │                                             │
│  │ Season Pass │ │                                             │
│  │ [████░░░░░] │ │                                             │
│  │ Level 5     │ │                                             │
│  └─────────────┘ │                                             │
└──────────────────┴─────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│               ⚡ QUICK ACTIONS (4-column grid)                │
│ [+ Submit] [👥 Teams] [📅 Create Event] [🏢 Book Space]      │
└────────────────────────────────────────────────────────────────┘

┌──────────────────────────┬──────────────────────────────────────┐
│                          │                                      │
│ 🎯 ACTIVE QUESTS         │ 🔔 RECENT UPDATES                   │
│ ┌────────────────────┐   │ ┌────────────────────────────────┐  │
│ │ Complete 5 Events  │   │ │ 📅 Assembly Approved            │  │
│ │ [██████░░] 3/5     │   │ │ You're invited to the event     │  │
│ │ +50 XP             │   │ │ 2 hours ago                     │  │
│ │ Daily              │   │ ├────────────────────────────────┤  │
│ └────────────────────┘   │ │ 🎯 Quest Completed              │  │
│ ┌────────────────────┐   │ │ You completed "5 Events"       │  │
│ │ Win a Game         │   │ │ +50 XP earned!                 │  │
│ │ [████████░░] 8/10  │   │ ├────────────────────────────────┤  │
│ │ +100 XP            │   │ │ ✨ Badge Unlocked               │  │
│ │ Weekly             │   │ │ Gold Star achievement earned!   │  │
│ └────────────────────┘   │ │ 1 day ago                       │  │
│ ┌────────────────────┐   │ └────────────────────────────────┘  │
│ │ Submit Homework    │   │                                      │
│ │ [██████████░░] 3/3 │   │ [View All Notifications →]          │
│ │ +25 XP             │   │                                      │
│ │ Daily (Resets 12h) │   │                                      │
│ └────────────────────┘   │                                      │
└──────────────────────────┴──────────────────────────────────────┘
```

---

## Component Gallery

### 1. **Top Navigation Bar**

```html
<!-- Structure -->
<nav class="sticky top-0 z-40 bg-white dark:bg-zinc-800 border-b">
  <div class="flex justify-between items-center h-16">
    <!-- Logo (left) -->
    <div class="flex items-center gap-2">[Logo Icon] [App Name]</div>

    <!-- Controls (right) -->
    <div class="flex items-center gap-4">
      [Theme Toggle] [Notifications] [Profile]
    </div>
  </div>
</nav>
```

**Styling Classes**:

- Container: `sticky top-0 z-40 bg-white dark:bg-zinc-800`
- Logo: `w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-xl`
- Icons: `w-5 h-5 text-zinc-600 dark:text-zinc-400`
- Buttons: `p-2 hover:bg-zinc-100 dark:hover:bg-zinc-700 rounded-lg`

---

### 2. **Mini Profile Card**

```html
<!-- Mobile -->
<div class="card p-6">
  <!-- Header -->
  <div class="flex items-center gap-4 mb-4">
    <img class="w-16 h-16 rounded-2xl" src="avatar" />
    <div>
      <h3 class="font-bold text-zinc-900">Name</h3>
      <p class="text-sm text-zinc-600">10A</p>
    </div>
  </div>

  <!-- Shanyraq -->
  <div class="mb-4 pb-4 border-b border-zinc-200 dark:border-zinc-700">
    <p class="text-xs text-zinc-500">Shanyraq</p>
    <p class="font-semibold">Team Name</p>
  </div>

  <!-- Rank Badge -->
  <div class="mb-4 flex items-center gap-2">
    <div class="rank-badge rank-gold">⭐</div>
    <div>
      <p class="text-xs text-zinc-500">Rank</p>
      <p class="font-semibold">Gold</p>
    </div>
  </div>

  <!-- Points Grid -->
  <div class="grid grid-cols-2 gap-3 mb-6">
    <div
      class="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/30 rounded-lg p-3"
    >
      <p class="text-xs text-emerald-700">Season Points</p>
      <p class="text-2xl font-bold text-emerald-900">350</p>
    </div>
    <div
      class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 rounded-lg p-3"
    >
      <p class="text-xs text-purple-700">Total XP</p>
      <p class="text-2xl font-bold text-purple-900">2850</p>
    </div>
  </div>

  <!-- Progress Bar -->
  <div>
    <div class="flex items-center justify-between mb-2">
      <p class="text-sm font-semibold">Season Pass</p>
      <p class="text-xs text-zinc-500">Level 5</p>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width: 62%"></div>
    </div>
    <p class="text-xs text-zinc-500 mt-2">350/1000 XP to next level</p>
  </div>
</div>
```

**Color Variants**:

- Rank Gold: `bg-gradient-to-br from-ffd700 to-ffb347`
- Rank Silver: `bg-gradient-to-br from-c0c0c0 to-a8a8a8`
- Rank Bronze: `bg-gradient-to-br from-cd7f32 to-a0522d`
- Rank Platinum: `bg-gradient-to-br from-e5e4e2 to-b8b8b8`

---

### 3. **Hall of Fame Carousel**

```html
<!-- Structure -->
<div class="card overflow-hidden">
  <div class="px-6 py-4 border-b border-zinc-200 dark:border-zinc-700">
    <h3 class="font-bold text-zinc-900 dark:text-zinc-100">🌟 Weekly Stars</h3>
  </div>

  <div class="overflow-x-auto">
    <div class="flex gap-4 p-6 min-w-full">
      <!-- Card (repeating) -->
      <a href="/profile/user-id" class="flex-shrink-0 w-32">
        <div class="card p-3 text-center hover:shadow-md transition-shadow">
          <!-- Avatar -->
          <img
            class="w-12 h-12 rounded-full object-cover mx-auto mb-2"
            src="avatar"
          />

          <!-- Name -->
          <p class="text-sm font-semibold text-zinc-900 truncate">Username</p>

          <!-- XP Delta -->
          <div class="mt-2 pt-2 border-t border-zinc-200">
            <p class="text-lg font-bold text-amber-600">+95</p>
            <span class="badge badge-warning text-xs mt-1">Weekly Star</span>
          </div>
        </div>
      </a>
      <!-- ... repeat for 5 students ... -->
    </div>
  </div>
</div>
```

**Carousel Features**:

- Horizontal scroll on mobile
- Fixed card width: `w-32`
- Flex shrink to prevent stretching: `flex-shrink-0`
- Smooth hover: `hover:shadow-md transition-shadow`

---

### 4. **Event Card (from Carousel)**

```html
<!-- Event Card Structure -->
<div class="card overflow-hidden hover:shadow-md transition-shadow">
  <!-- Header with Image -->
  <div class="h-32 bg-gradient-to-br from-indigo-400 to-indigo-600 relative">
    <span class="badge badge-success absolute top-2 left-2">Approved</span>
  </div>

  <!-- Event Details -->
  <div class="p-4">
    <!-- Title -->
    <h4 class="font-bold text-zinc-900 dark:text-zinc-100 mb-3 line-clamp-2">
      Event Title
    </h4>

    <!-- Date/Time/Location -->
    <div class="space-y-2 mb-4 text-sm text-zinc-600 dark:text-zinc-400">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4"><!-- calendar icon --></svg>
        <span>Jan 31, 2026</span>
      </div>
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4"><!-- clock icon --></svg>
        <span>14:30</span>
      </div>
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4"><!-- location icon --></svg>
        <span>Main Hall</span>
      </div>
    </div>

    <!-- CTA Button -->
    <button class="btn btn-primary w-full text-sm">
      View Event
      <svg class="w-4 h-4 ml-2"><!-- arrow icon --></svg>
    </button>
  </div>
</div>
```

**Variants**:

- Pending: `badge badge-warning` (yellow)
- Approved: `badge badge-success` (green)
- Rejected: `badge badge-danger` (red)

---

### 5. **Quick Action Button**

```html
<!-- Single Action Button -->
<a
  href="{% url 'opportunities:submit' %}"
  class="btn btn-ghost p-4 flex flex-col items-center justify-center gap-2 h-24 
          hover:bg-emerald-50 dark:hover:bg-emerald-900/20 
          border border-zinc-200 dark:border-zinc-700 
          hover:border-emerald-300 dark:hover:border-emerald-700 
          transition-all rounded-lg"
>
  <!-- Icon -->
  <svg class="w-6 h-6 text-emerald-600 dark:text-emerald-400">
    <!-- action icon -->
  </svg>

  <!-- Label -->
  <span class="text-sm font-medium text-zinc-900 dark:text-zinc-100">
    Submit Activity
  </span>
</a>
```

**Color Variants**:

- Submit: Green (`emerald`)
- Teams: Purple (`purple`)
- Create: Blue (`blue`)
- Book: Orange (`orange`)

---

### 6. **Quest Card**

```html
<!-- Quest Item (in list) -->
<div class="p-4 hover:bg-zinc-50 dark:hover:bg-zinc-700/50 transition-colors">
  <!-- Header -->
  <div class="flex items-start justify-between mb-2">
    <h4 class="font-semibold text-zinc-900 dark:text-zinc-100">Quest Title</h4>
    <span class="badge badge-info text-xs">Daily</span>
  </div>

  <!-- Description -->
  <p class="text-sm text-zinc-600 dark:text-zinc-400 mb-3">
    Quest description text
  </p>

  <!-- Progress -->
  <div class="mb-2">
    <div class="flex items-center justify-between mb-1">
      <span class="text-xs text-zinc-600 dark:text-zinc-400">3/5</span>
      <span class="text-xs font-medium text-emerald-600 dark:text-emerald-400">
        +50 XP
      </span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width: 60%"></div>
    </div>
  </div>

  <!-- Reset Time -->
  <p class="text-xs text-zinc-500 dark:text-zinc-400">Resets in ~12 hours</p>
</div>
```

---

### 7. **Notification Card**

```html
<!-- Notification Item (in list) -->
<div class="p-4 hover:bg-zinc-50 dark:hover:bg-zinc-700/50 transition-colors">
  <div class="flex gap-3">
    <!-- Icon -->
    <div
      class="flex-shrink-0 w-8 h-8 rounded-full 
                bg-emerald-100 dark:bg-emerald-900/30 
                flex items-center justify-center 
                text-emerald-600 dark:text-emerald-400"
    >
      📅
    </div>

    <!-- Content -->
    <div class="flex-1">
      <h4 class="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
        Notification Title
      </h4>
      <p class="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
        Notification message text
      </p>
      <p class="text-xs text-zinc-400 dark:text-zinc-500 mt-2">2 hours ago</p>
    </div>
  </div>
</div>
```

**Icon Types**:

- Event: 📅
- Quest: 🎯
- Team: 👥
- Other: ✨

---

### 8. **Badge Styles**

```html
<!-- Badge Component -->
<span class="badge badge-success">Success</span>

<span class="badge badge-warning">Warning</span>

<span class="badge badge-danger">Danger</span>

<span class="badge badge-info">Info</span>
```

**CSS Classes**:

```css
.badge-success  /* Green: bg-dcfce7 text-166534 */
.badge-warning  /* Yellow: bg-fef3c7 text-92400e */
.badge-danger   /* Red: bg-fee2e2 text-991b1b */
.badge-info     /* Blue: bg-dbeafe text-1e40af */
```

---

### 9. **Progress Bar**

```html
<!-- Basic Progress Bar -->
<div class="progress-bar">
  <div class="progress-fill" style="width: 65%"></div>
</div>

<!-- With Label -->
<div>
  <div class="flex items-center justify-between mb-1">
    <span class="text-xs font-medium">Progress</span>
    <span class="text-xs text-zinc-500">65%</span>
  </div>
  <div class="progress-bar">
    <div class="progress-fill" style="width: 65%"></div>
  </div>
</div>
```

**CSS Classes**:

```css
.progress-bar {
  width: 100%;
  height: 0.5rem;
  background: #e5e7eb; /* light gray */
  border-radius: 9999px;
}

.progress-fill {
  background: var(--primary-gradient); /* emerald gradient */
  border-radius: 9999px;
  transition: width 0.3s ease;
}
```

---

### 10. **Rank Badges**

```html
<!-- Rank Badge Component -->
<div class="rank-badge rank-gold">⭐</div>

<div class="rank-badge rank-silver">🥈</div>

<div class="rank-badge rank-bronze">🥉</div>

<div class="rank-badge rank-platinum">👑</div>
```

**CSS Classes**:

```css
.rank-badge {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.125rem;
  color: white;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
}

.rank-silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a8a8a8 100%);
}

.rank-bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
}

.rank-platinum {
  background: linear-gradient(135deg, #e5e4e2 0%, #b8b8b8 100%);
}
```

---

### 11. **Skeleton Loader**

```html
<!-- Skeleton Loading State -->
<div class="flex-shrink-0 w-32">
  <div class="card p-3">
    <div class="skeleton w-12 h-12 rounded-full mx-auto mb-2"></div>
    <div class="skeleton h-4 w-full mb-2"></div>
    <div class="skeleton h-3 w-3/4 mx-auto"></div>
  </div>
</div>

<!-- Single Line Skeleton -->
<div class="skeleton h-4 w-3/4"></div>

<!-- Text Skeleton (Multiple Lines) -->
<div class="space-y-2 mb-4">
  <div class="skeleton h-4 w-full"></div>
  <div class="skeleton h-4 w-5/6"></div>
  <div class="skeleton h-4 w-4/5"></div>
</div>
```

**CSS Classes**:

```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 0.5rem;
}
```

---

## Responsive Breakpoints

```html
<!-- Mobile (< 768px) -->
<div class="grid grid-cols-1 gap-6">
  <!-- Single column layout -->
</div>

<!-- Tablet (768px - 1024px) -->
<div class="grid grid-cols-2 gap-6">
  <!-- Two column layout -->
</div>

<!-- Desktop (> 1024px) -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <!-- Three column layout -->
</div>

<!-- Large Desktop (> 1280px) -->
<!-- Same as desktop with more whitespace -->
```

---

## Dark Mode Examples

```html
<!-- Light Mode (default) -->
<div class="bg-white text-zinc-900 border-zinc-200">Light theme styling</div>

<!-- Dark Mode (with dark: prefix) -->
<div
  class="bg-white dark:bg-zinc-800 
            text-zinc-900 dark:text-zinc-100 
            border-zinc-200 dark:border-zinc-700"
>
  Responds to dark mode
</div>

<!-- Always Light (ignore dark mode) -->
<div class="bg-white text-zinc-900">Always light</div>
```

---

## Color Palette

### Primary Colors

- **Emerald (Green)**: `#10b981` / `from-emerald-400 to-emerald-600`
- **Purple**: `#6366f1` / `from-purple-400 to-purple-600`
- **Indigo**: `#4f46e5` / `from-indigo-400 to-indigo-600`
- **Orange**: `#f97316` / `from-orange-400 to-orange-600`

### Neutral Colors

- **Light**: `#f9fafb` (zinc-50)
- **White**: `#ffffff`
- **Gray**: `#d4d4d8` to `#71717a` (zinc-300 to zinc-500)
- **Dark**: `#18181b` to `#27272a` (zinc-900 to zinc-800)

### Status Colors

- **Success**: `#10b981` (emerald-600)
- **Warning**: `#eab308` (amber-400)
- **Danger**: `#ef4444` (red-500)
- **Info**: `#3b82f6` (blue-500)

---

## Font Sizes & Weights

| Use Case       | Size    | Weight         | Class                   |
| -------------- | ------- | -------------- | ----------------------- |
| Headings       | 24-32px | 700 (bold)     | `text-2xl font-bold`    |
| Section Titles | 18-20px | 600 (semibold) | `text-lg font-semibold` |
| Card Titles    | 16px    | 600 (semibold) | `font-semibold`         |
| Body Text      | 14-16px | 400 (normal)   | `text-sm text-zinc-600` |
| Labels         | 12-14px | 500 (medium)   | `text-xs font-medium`   |
| Small Text     | 12px    | 400 (normal)   | `text-xs text-zinc-400` |

---

## Spacing Guidelines

| Element      | Spacing | Class       |
| ------------ | ------- | ----------- |
| Card padding | 24px    | `p-6`       |
| Section gap  | 24px    | `gap-6`     |
| Element gap  | 16px    | `gap-4`     |
| Small gap    | 8px     | `gap-2`     |
| Margins      | 16-24px | `mb-4 mb-6` |

---

## Animation Guide

### Progress Bar Animation

```css
.progress-fill {
  transition: width 0.3s ease;
}
```

### Card Hover

```css
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}
```

### Skeleton Shimmer

```css
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton {
  animation: shimmer 1.5s infinite;
}
```

---

## Accessibility Features

- ✅ Semantic HTML (`<nav>`, `<main>`, `<article>`)
- ✅ ARIA labels on icons (`aria-label="..."`)
- ✅ Color contrast > 4.5:1
- ✅ Focus visible on buttons
- ✅ Keyboard navigation (Tab, Enter)
- ✅ Alt text on images
- ✅ Logical tab order

---

## Performance Notes

- **CSS**: 20KB minified (TailwindCSS)
- **JavaScript**: ~5KB (Alpine.js)
- **Images**: Lazy loaded with fallbacks
- **Fonts**: System fonts (no web fonts)
- **Rendering**: Server-side (fast initial load)

---

**Version**: 1.0.0  
**Last Updated**: January 31, 2026  
**Status**: ✅ Production Ready
