# Moderation App

The Moderation app provides a comprehensive dashboard for managing school approvals and administrative tasks in the NIS SuperApp.

## Features

### Admin Dashboard

- **Kanban-style approval board** for pending events and space bookings
- **Statistics overview** showing pending items and system metrics
- **Recent moderator actions log** for audit trail
- **Quick action buttons** for common moderation tasks

### Approval Queues

- **Pending Events**: Review and approve/reject school events
- **Pending Space Bookings**: Manage classroom and facility bookings
- **Manual Point Control**: Add/revoke points for users (via admin interface)
- **User Management**: View and manage user accounts
- **Shanyraq Management**: Manage house groups and memberships

### Moderator Actions Log

- Complete audit trail of all moderation actions
- Tracks who performed what action and when
- Includes old/new values for transparency
- Searchable and filterable log entries

## Access

The moderation dashboard is available at `/moderation/dashboard/` and requires moderator privileges (staff status or teacher/admin role).

## Usage

1. **Login** as a moderator (teacher or admin)
2. **Navigate** to the moderation dashboard
3. **Review** pending items in the kanban board
4. **Approve/Reject** items with optional comments
5. **Monitor** recent actions in the activity log

## Test Data

To create test data for development:

```bash
python manage.py create_test_data
```

This creates:

- Test moderator account: `moderator@nis.kz` / `password123`
- Pending event and space booking for testing
- Sample shanyraq and user data

## Technical Details

- Uses Django's custom AdminSite for isolated moderation interface
- Integrates with existing events, spaces, accounts, and shanyraq apps
- Responsive design with TailwindCSS styling
- AJAX-powered approval actions with modal confirmations
