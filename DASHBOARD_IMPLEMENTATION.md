# NIS SuperApp Dashboard Implementation Guide

## Overview

The Home/Dashboard page (`templates/core/home.html`) is the main entry point for authenticated users in the NIS SuperApp. It provides a comprehensive, gamified overview of school activities with a modern Supercell-inspired design.

## Architecture

### Backend (Django View)

**File**: `apps/core/views.py`

The `HomeView` class handles all context data for the dashboard:

```python
class HomeView(BaseTemplateMixin, TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        # Provides: user_profile, weekly_hall_of_fame, upcoming_events,
        # active_quests, recent_notifications, unread_notifications_count
```

### Frontend Template

**File**: `templates/core/home.html`

The template is built with:

- **TailwindCSS**: Utility-first responsive styling
- **Alpine.js**: Client-side interactions (theme toggle, carousels)
- **Mobile-first**: Adapts seamlessly from mobile to desktop

## Template Sections

### 1. **Top Navigation Bar**

- **Logo & Brand**: "NIS SuperApp" with app icon
- **Theme Toggle**: Light/Dark mode switcher
- **Notification Bell**: Shows unread notification badge
- **Profile Menu**: Quick access to user profile

**Components**:

- Navigation bar is sticky and always visible
- Icons are SVG-based and scalable
- Responsive flex layout for mobile

### 2. **Mini Profile Card**

Located in the left sidebar on desktop (full width on mobile).

**Displays**:

- User avatar (or gradient placeholder)
- Full name & class
- Shanyraq name (if assigned)
- Rank badge with emoji (Gold ⭐, Silver 🥈, Bronze 🥉, Platinum 👑)
- Season Points (Shanyraq-specific)
- Total XP (Lifetime NIS points)
- Season Pass progress bar

**Interactions**:

- Clickable card links to full profile
- Hover effect with shadow lift
- Progress bar animated on load

**Data Source**: `UserProfile` model

### 3. **Weekly Stars (Hall of Fame Carousel)**

Horizontal scrolling carousel showing top 5 students by weekly XP growth.

**Features**:

- Avatar with fallback gradient placeholder
- Name (truncated)
- Weekly XP delta (+Δ points)
- "Weekly Star" badge
- Skeleton loaders while loading

**Interactions**:

- Click to view student profile
- Smooth horizontal scroll on mobile
- Link to full leaderboard

**Data Source**: `UserProfile.NIS_points` (ranked)

### 4. **Upcoming Events Carousel**

Shows next 7 days of approved events in a carousel format.

**Event Card Includes**:

- Event title
- Start date (M d, Y format)
- Start time (H:i format)
- Location
- Status badge (Approved/Pending)
- "View Event" button

**Interactions**:

- Click to view event details
- Status-based badge styling
- Responsive card sizing

**Data Source**: `Event` model (filtered by `start_at`, `status='approved'`)

### 5. **Quick Actions Grid**

Four-column grid (2 columns on mobile) with touch-friendly action buttons.

**Buttons**:

- **Submit Activity**: Goes to opportunities submission
- **Find a Team**: Links to team discovery
- **Create Event**: (Student Council only) Event creation form
- **Book a Space**: Space reservation system

**Design**:

- Large icon + label
- Hover color changes per action
- Rounded borders with hover effects
- Responsive grid layout

### 6. **Active Quests Preview**

Shows 3-5 current daily/weekly/milestone quests.

**Each Quest Card Shows**:

- Quest title
- Quest type badge (Daily/Weekly/Milestone)
- Description (truncated)
- Progress bar (0-100%)
- Current progress vs. target (e.g., "2/5")
- XP reward
- Reset time for daily quests

**Interactions**:

- Click to view Season Pass page
- Progress bar updates dynamically
- Empty state with link to all quests

**Data Source**: `Quest` + `UserQuestProgress` models

### 7. **Recent Notifications/Updates**

Shows last 3 notifications with type-specific icons.

**Notification Card**:

- Type-specific emoji icon (📅 event, 🎯 quest, 👥 team, ✨ other)
- Title
- Message (truncated)
- Relative timestamp ("5 minutes ago")

**Interactions**:

- Hover highlighting
- Link to notifications page
- Empty state messaging

**Data Source**: `Notification` model

## Context Data Structure

The view provides the following context variables:

```python
{
    'user_profile': UserProfile,  # Current user's extended profile
    'weekly_hall_of_fame': [      # List of top 5 weekly performers
        {
            'user': User,
            'delta_points': int
        },
        ...
    ],
    'upcoming_events': QuerySet,   # Events in next 7 days
    'active_quests': QuerySet,     # Active quests with user progress
    'recent_notifications': QuerySet,  # Last 3 notifications
    'unread_notifications_count': int  # Badge count
}
```

## Key Features

### 1. **Responsive Design**

- **Mobile (< 768px)**: Single column layout
- **Tablet (768px - 1024px)**: Two columns
- **Desktop (> 1024px)**: Three column grid with sidebar

### 2. **Performance**

- Server-side rendering for fast initial load
- Skeleton loaders for carousels
- Lazy loading placeholders
- Database query optimization with `select_related()` and `prefetch_related()`

### 3. **Gamification**

- **XP Display**: Season and lifetime points prominent
- **Rank Badges**: Visual rank representation
- **Progress Bars**: Animated on scroll
- **Weekly Leaderboard**: Competitive element
- **Quest Progress**: Motivating challenges

### 4. **Accessibility**

- Semantic HTML structure
- ARIA labels on buttons and icons
- Keyboard navigation support
- Dark mode support with `dark:` classes
- Color contrast compliance

### 5. **Dark Mode**

- Toggle in top navigation
- Persistent (localStorage)
- All components support both themes
- `dark:` Tailwind utilities throughout

## Customization

### Modify Dashboard Colors

Edit CSS variables in `static/css/design-system.css`:

```css
:root {
  --primary-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
  --secondary-gradient: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  /* ... */
}
```

### Change Layout Grid

Modify grid classes in `templates/core/home.html`:

```html
<!-- Desktop: 3 columns (1 profile + 2 content) -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <!-- Profile: 1 column -->
  <div class="lg:col-span-1">...</div>

  <!-- Content: 2 columns -->
  <div class="lg:col-span-2">...</div>
</div>
```

### Add/Remove Sections

All sections are self-contained divs. To remove a section, delete the corresponding `<div class="card">` block.

## Data Flow

```
Request to /
    ↓
HomeView.get_context_data()
    ├─ Fetch UserProfile
    ├─ Query UserProfile (weekly rankings)
    ├─ Query Event (next 7 days)
    ├─ Query Quest + UserQuestProgress
    ├─ Query Notification (recent)
    └─ Count unread Notification
    ↓
Template Rendering
    ├─ TailwindCSS styles
    ├─ Alpine.js enhancements
    ├─ Server-side HTML generation
    └─ Client-side interactivity
    ↓
Browser Display
```

## Database Queries

The view executes the following queries:

1. **UserProfile**: Get current user's profile
2. **UserProfile** (weekly): Get top 5 by NIS_points
3. **Event**: Get next 7 days of approved events
4. **Quest**: Get active quests
5. **UserQuestProgress**: Get user's quest progress
6. **Notification**: Get recent notifications
7. **Notification**: Count unread

**Optimization**:

- Uses `select_related('user')` to prevent N+1 queries
- Uses `prefetch_related('user_progress')` for quest progress
- Filters at DB level for events and notifications

## Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Alpine.js Features

Currently used for:

- Theme toggle interaction
- Notification badge display
- Hover states
- Future: Real-time quest updates

## SEO & Meta Tags

Inherits from `base.html`:

- Page title: "Dashboard – NIS SuperApp"
- Mobile viewport meta tag
- Canonical URL

## Testing

To test the dashboard:

1. **Create a test user**: Sign up with `@nis.edu.kz` email
2. **Add profile data**: Complete profile with avatar, class, shanyraq
3. **Create test events**: Add approved events within 7 days
4. **Create test quests**: Add active quests to season
5. **Visit dashboard**: Navigate to `/` (home page)

## Troubleshooting

| Issue                    | Solution                                                |
| ------------------------ | ------------------------------------------------------- |
| Empty hall of fame       | Create more users and assign XP points                  |
| No events showing        | Create events with `status='approved'` and future dates |
| Missing progress bars    | Ensure UserQuestProgress records exist                  |
| Dark mode not working    | Check localStorage for `theme` key                      |
| Skeleton loaders visible | Data loading - wait for queries to complete             |

## Related Files

- `apps/accounts/models.py`: UserProfile model
- `apps/events/models.py`: Event model
- `apps/season/models.py`: Quest, UserQuestProgress models
- `apps/notifications/models.py`: Notification model
- `static/css/design-system.css`: Design system components
- `templates/base.html`: Base layout with theme toggle

## Future Enhancements

- [ ] Real-time notifications using WebSockets
- [ ] Personalized recommendations based on user interests
- [ ] Dark mode toggle persistence (currently in localStorage)
- [ ] Achievements unlock animations
- [ ] Animated counters for XP/points
- [ ] Skeleton loading states for each section
- [ ] Analytics dashboard for organizers
- [ ] Customizable widget layout (drag & drop)
