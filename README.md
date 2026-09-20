# RoomFinder - Find Your Perfect Room

A full-stack room rental and property finding web application built with Django, HTML, CSS, and JavaScript.

## Features

- **User Authentication**: Register, Login, Profile management
- **Property Listings**: Search, filter, view details of rooms, apartments, houses
- **Map Integration**: Interactive map view of properties
- **Favorites**: Save rooms for later
- **Bookings & Visits**: Schedule property visits
- **Real-time Messaging**: WebSocket chat between tenants and owners (typing indicators, presence, auto-reconnect)
- **Reviews & Ratings**: Rate and review properties
- **Owner Dashboard**: Manage properties, view inquiries
- **Tenant Dashboard**: Saved rooms, visits, messages
- **Responsive Design**: Works on mobile, tablet, desktop

## Tech Stack

- **Backend**: Python Django 4.2+ with Django Channels
- **Real-time**: WebSockets via Channels + Daphne (InMemory layer for dev; Redis for production)
- **Database**: SQLite (default), easily switchable to PostgreSQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with modern responsive design
- **Images**: Pillow for image handling

## Project Structure

```
Room Finder/
├── backend/                 # Django project
│   ├── manage.py
│   ├── roomfinder/          # Project settings
│   ├── accounts/            # User auth & profiles
│   ├── properties/          # Property listings
│   ├── bookings/            # Visit bookings
│   ├── favorites/           # Saved properties
│   ├── reviews/             # Ratings & reviews
│   └── messaging/           # Chat system
├── frontend/
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
├── media/                   # User uploaded files
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone & Navigate
```bash
cd "Room Finder"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Collect Static Files (optional for production)
```bash
python manage.py collectstatic
```

### 7. Run Development Server

Because of WebSockets, use Daphne (or `runserver` with `daphne` in `INSTALLED_APPS`):

```bash
# Option A – Django runserver (works with Channels when daphne is installed)
python manage.py runserver

# Option B – Daphne ASGI server (recommended for WebSockets)
daphne -b 0.0.0.0 -p 8000 roomfinder.asgi:application
```

Visit: http://127.0.0.1:8000/

### WebSocket Chat

- Endpoint: `ws://127.0.0.1:8000/ws/chat/<conversation_id>/`
- Features: live messages, typing indicators, online/offline presence, auto-reconnect, HTTP fallback
- Development uses **InMemoryChannelLayer** (no Redis needed)
- For production, install Redis and switch `CHANNEL_LAYERS` in `settings.py` to `channels_redis`

## Default Roles

- **Tenant**: Search rooms, save favorites, book visits, message owners
- **Owner**: List properties, manage inquiries, respond to messages
- **Admin**: Full access via Django admin

## Environment Variables (Optional)

Create a `.env` file in the backend folder:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## License

MIT License - Feel free to use and modify.
