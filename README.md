# NIS SuperApp

Django monolith MVP for the hackathon.

## Tech stack

- Django 5.x
- SQLite3
- TailwindCSS (CDN) + Alpine.js
- Django Templates
- django-allauth
- Django Admin for moderation

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env and set SECRET_KEY
cp .env.example .env

# Migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Project layout

```
NIS_SuperApp/
├── config/                 # Project config
│   ├── settings/            # Env-based settings (base, development, production, test)
│   ├── urls.py
│   └── wsgi.py, asgi.py
├── apps/
│   ├── accounts/            # Custom User, Role
│   ├── core/                # enums, mixins, permissions, services
│   ├── shanyraq/
│   ├── events/
│   ├── spaces/
│   ├── opportunities/
│   ├── teams/
│   ├── season/
│   ├── moderation/
│   └── notifications/
├── templates/               # Global templates (base.html)
├── static/
├── manage.py
└── requirements.txt
```

## Environment

Set `DJANGO_ENV=development|production|test`. Default is `development`.
