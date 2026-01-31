# Dashboard Quick Start Guide

## What You're Getting

A production-ready, gamified home dashboard for NIS SuperApp with:

✅ **Responsive Design** - Mobile-first, works on all devices  
✅ **Dark/Light Mode** - Theme toggle in navbar  
✅ **Gamification Elements** - XP, ranks, leaderboards, quests  
✅ **Real-time Data** - Server-rendered, no loading delays  
✅ **Accessibility** - WCAG compliant, keyboard navigation  
✅ **Performance Optimized** - Efficient database queries, caching-ready

---

## File Structure

```
NIS_SuperApp/
├── templates/core/home.html          # Main dashboard template
├── apps/core/views.py                # Dashboard view & context data
├── apps/notifications/
│   ├── models.py                     # New Notification model
│   └── admin.py                      # Admin registration
├── static/css/design-system.css      # Component library
└── DASHBOARD_IMPLEMENTATION.md       # Full documentation
```

---

## Page Sections Overview

### 🎯 At-a-Glance Layout

```
┌─────────────────────────────────────────────────────────┐
│  Logo  Theme Toggle  Notification Bell  Profile Menu    │ ← Top Nav
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Welcome back, [Name]! 👋                                │
├──────────────────────┬──────────────────────────────────┤
│   Mini Profile       │  Weekly Stars (Hall of Fame)     │
│   Card               │  ────────────────────────────    │
│   - Avatar           │  Upcoming Events Carousel        │
│   - Rank             │  ────────────────────────────    │
│   - Points/XP        │                                  │
│   - Progress Bar     │                                  │
└──────────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ⚡ Quick Actions Grid                                   │
│  [Submit] [Teams] [Create Event] [Book Space]           │
└─────────────────────────────────────────────────────────┘

┌──────────────────────────┬──────────────────────────────┐
│  🎯 Active Quests        │  🔔 Recent Updates           │
│  - Quest 1 [██████░░]    │  - Notification 1            │
│  - Quest 2 [████░░░░░░]  │  - Notification 2            │
│  - Quest 3 [████████░░]  │  - Notification 3            │
└──────────────────────────┴──────────────────────────────┘
```

---

## Key Components

### 1. Mini Profile Card

**Location**: Left sidebar / Top on mobile

Shows:

- User avatar with fallback
- Name & class
- Shanyraq name
- Current rank (with emoji badge)
- Season points & total XP
- Season pass progress bar

**Interaction**: Click to go to full profile

### 2. Weekly Stars Carousel

**Location**: Top right content area

Shows:

- Top 5 students by weekly XP growth
- Horizontal scroll on mobile
- Click to view profile

### 3. Upcoming Events Carousel

**Location**: Under weekly stars

Shows:

- Next 7 days of approved events
- Date, time, location
- Status badge
- "View Event" button

### 4. Quick Actions Grid

**Location**: Below carousels

4 touch-friendly buttons:

- Submit Activity → `opportunities:submit`
- Find a Team → `teams:list`
- Create Event → `events:create` (Student Council only)
- Book a Space → `spaces:list`

### 5. Active Quests

**Location**: Bottom left (2-column layout)

Shows:

- Up to 5 active quests
- Progress bar with current/target
- XP reward
- Type badge (Daily/Weekly/Milestone)
- Reset time for daily quests

### 6. Recent Updates/Notifications

**Location**: Bottom right (2-column layout)

Shows:

- Last 3 notifications
- Type-specific icons
- Truncated message
- Relative timestamp

---

## Data Requirements

### User Profile

```python
UserProfile:
  - avatar (optional image)
  - full_name
  - class_name (e.g., "10A")
  - shanyraq (FK to Shanyraq)
  - NIS_points (lifetime XP)
  - shanyraq_points (season XP)
  - rank (e.g., "Gold")
```

### Events

```python
Event:
  - title
  - start_at (DateTime)
  - location (optional)
  - status = 'approved'
```

### Quests

```python
Quest:
  - title
  - description
  - target (int)
  - xp_reward
  - quest_type ('daily'|'weekly'|'milestone')
  - is_active = True

UserQuestProgress:
  - user (FK)
  - quest (FK)
  - current_progress
  - completed_at (optional)
```

### Notifications

```python
Notification:
  - user (FK)
  - title
  - message
  - notification_type
  - is_read
  - created_at
```

---

## Styling & Customization

### Colors

Edit `static/css/design-system.css`:

```css
:root {
  --primary-gradient: linear-gradient(...); /* Green */
  --secondary-gradient: linear-gradient(...); /* Purple */
  --accent-purple: linear-gradient(...);
  --accent-orange: linear-gradient(...);
}
```

### Typography

Dashboard uses:

- **Headings**: Bold, 24-32px
- **Body**: Regular, 14-16px
- **Labels**: Semibold, 12-14px

### Responsive Breakpoints

- **Mobile**: < 768px (1 column)
- **Tablet**: 768px - 1024px (2 columns)
- **Desktop**: > 1024px (3 columns + sidebar)

### Dark Mode

- Uses Tailwind's `dark:` prefix
- Toggle stores in localStorage
- Applies to `<html>` element class

---

## Integration Points

### URL Routing

Dashboard is already registered as the home page at `/`:

```python
# config/urls.py
path('', include('apps.core.urls')),  # → / (home)

# apps/core/urls.py
path('', views.HomeView.as_view(), name='home')
```

### View Context Variables

The template expects:

```python
{
    'user_profile': UserProfile instance,
    'weekly_hall_of_fame': List[{user, delta_points}],
    'upcoming_events': QuerySet[Event],
    'active_quests': QuerySet[Quest],
    'recent_notifications': QuerySet[Notification],
    'unread_notifications_count': int
}
```

### Required URLs

Dashboard links to:

- `accounts:profile` - User profile page
- `accounts:leaderboard` - Full leaderboard
- `accounts:notifications` - All notifications
- `events:list` - All events
- `events:create` - Event creation (Student Council)
- `events:detail` - Event details
- `teams:list` - Team discovery
- `spaces:list` - Space booking
- `opportunities:submit` - Activity submission
- `season:quests` - All quests

Make sure these URL names are defined in your `urls.py` files.

---

## Testing Checklist

- [ ] Create test user with `@nis.edu.kz` email
- [ ] Add user avatar and class name
- [ ] Assign user to a Shanyraq
- [ ] Create test events (upcoming, approved)
- [ ] Create test quests (active)
- [ ] Create test notifications
- [ ] Verify all cards display correctly
- [ ] Test dark mode toggle
- [ ] Test responsive layout on mobile
- [ ] Verify all links work
- [ ] Check performance (queries < 2s)

---

## Performance Notes

### Database Queries

The view makes ~7 queries:

1. User authentication check
2. Get user profile
3. Get top students (hall of fame)
4. Get upcoming events
5. Get active quests
6. Get user quest progress
7. Get recent notifications

**Optimization**: Uses `select_related()` and `prefetch_related()` to minimize N+1 queries.

### Caching Opportunities

Consider caching:

- Hall of fame (update daily)
- Upcoming events (update hourly)
- Active quests (update on quest change)

### Frontend Performance

- No external API calls
- All data server-rendered
- Minimal JavaScript
- Optimized CSS (~20KB)

---

## Security

- ✅ User must be authenticated (`@login_required`)
- ✅ Personal data only shown to user
- ✅ Notifications only visible to recipient
- ✅ XSS protected with Django template escaping
- ✅ CSRF tokens on any future forms

---

## Troubleshooting

**Q: Dashboard shows empty sections**
A: Make sure you have test data:

```python
python manage.py shell
from apps.accounts.models import UserProfile
UserProfile.objects.create(user=user, NIS_points=100, class_name="10A")
```

**Q: Hall of fame not showing**
A: Ensure UserProfile records have NIS_points > 0:

```python
UserProfile.objects.update(NIS_points=50)
```

**Q: Events carousel empty**
A: Create events with status='approved' in the future:

```python
from apps.events.models import Event
from django.utils import timezone
Event.objects.create(
    title="School Assembly",
    start_at=timezone.now() + timedelta(days=1),
    status='approved'
)
```

**Q: Dark mode not persisting**
A: Check browser localStorage, ensure JavaScript is enabled

**Q: Quests not showing progress**
A: Verify UserQuestProgress records exist:

```python
from apps.season.models import UserQuestProgress
UserQuestProgress.objects.create(user=user, quest=quest, current_progress=1)
```

---

## Next Steps

1. **Populate Test Data**
   - Create sample users, events, quests
   - Set up leaderboard data

2. **Add Real-time Features** (Optional)
   - WebSocket notifications
   - Live leaderboard updates
   - Real-time quest progress

3. **Customize Branding**
   - Update logo
   - Change color scheme
   - Add school logo

4. **Analytics**
   - Track dashboard visits
   - Monitor engagement metrics
   - Optimize based on user behavior

5. **Mobile App**
   - Export as PWA
   - Native app wrapper

---

## Files Modified/Created

**New Files**:

- `DASHBOARD_IMPLEMENTATION.md` - Full documentation
- `apps/notifications/migrations/0001_initial.py` - Notification model migration

**Modified Files**:

- `templates/core/home.html` - Complete dashboard template
- `apps/core/views.py` - Dashboard view with context
- `apps/notifications/models.py` - Notification model
- `apps/notifications/admin.py` - Admin registration
- `static/css/design-system.css` - Existing (maintained)
- `templates/account/login.html` - Existing (maintained)
- `templates/account/signup.html` - Existing (maintained)

---

## Support & Questions

For issues or questions:

1. Check `DASHBOARD_IMPLEMENTATION.md` for details
2. Review Django/Tailwind documentation
3. Check console for JavaScript errors
4. Verify database has test data

Happy coding! 🚀
