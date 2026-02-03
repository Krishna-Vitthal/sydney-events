# Sydney Events - Full Stack Application

A production-ready web application that automatically scrapes and displays events happening in Sydney, Australia.

## 🌟 Features

### Event Scraping & Auto Updates
- **Automatic scraping** from multiple event sources (Eventbrite, Meetup, Sydney Opera House, Time Out Sydney)
- **Scheduled updates** every 6 hours to keep events fresh
- **Change detection** - identifies new, updated, and inactive events
- **Content hashing** for efficient update detection

### Event Listing Website
- **Beautiful, responsive UI** built with React and Tailwind CSS
- **Event cards** showing title, date, venue, description, and source
- **Search & filters** - filter by keyword, date range, status, and source
- **"Get Tickets" flow** - collects user email with consent before redirecting to event source

### Admin Dashboard (Requires Google OAuth)
- **Google OAuth authentication**
- **Statistics overview** - total events, new, updated, inactive, imported counts
- **Table view** with sorting and filtering
- **Event preview panel** - full event details on click
- **Import functionality** - mark events as imported with notes
- **Status tags** - new, updated, inactive, imported

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

### Setup & Run

1. **Configure Google OAuth** (required for dashboard access):
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create a new OAuth 2.0 Client ID
   - Add authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
   - Copy credentials to `backend/.env`:
     ```
     GOOGLE_CLIENT_ID=your_client_id
     GOOGLE_CLIENT_SECRET=your_client_secret
     ```

2. **Run the application**:
   ```powershell
   # Simply run the start script
   .\start.ps1
   ```

   This will:
   - Create Python virtual environment
   - Install backend dependencies
   - Install frontend dependencies
   - Start both servers in separate windows

3. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
sydney-events/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   │   ├── auth.py     # Google OAuth
│   │   │   ├── events.py   # Events CRUD
│   │   │   └── scraper.py  # Scraper controls
│   │   ├── scrapers/       # Event scrapers
│   │   │   ├── base.py     # Base scraper class
│   │   │   ├── eventbrite.py
│   │   │   ├── meetup.py
│   │   │   ├── sydney_opera.py
│   │   │   ├── timeout.py
│   │   │   └── scraper_manager.py
│   │   ├── auth.py         # JWT authentication
│   │   ├── config.py       # Settings
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── api/           # API client
│   │   ├── store/         # Zustand state
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── start.ps1              # PowerShell startup script
└── README.md
```

## 🔧 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async ORM with SQLite
- **BeautifulSoup4** - HTML parsing for scraping
- **aiohttp** - Async HTTP client
- **APScheduler** - Background task scheduling
- **python-jose** - JWT tokens

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animations
- **Zustand** - State management
- **Headless UI** - Accessible components
- **Heroicons** - Beautiful icons

## 📝 API Endpoints

### Public Endpoints
- `GET /api/events/` - List events with filters
- `GET /api/events/{id}` - Get event details
- `GET /api/events/sources` - List event sources
- `POST /api/events/ticket-lead` - Submit email for tickets
- `GET /api/scraper/status` - Scraper status

### Protected Endpoints (requires authentication)
- `GET /api/auth/google/login` - Initiate Google OAuth
- `GET /api/auth/me` - Get current user
- `GET /api/events/stats` - Dashboard statistics
- `POST /api/events/{id}/import` - Import event
- `DELETE /api/events/{id}/import` - Remove import
- `POST /api/scraper/run` - Trigger manual scrape
- `GET /api/scraper/logs` - Scrape history

## 🔒 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | - |
| `SECRET_KEY` | JWT signing key | - |
| `DATABASE_URL` | SQLite database path | `sqlite+aiosqlite:///./events.db` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `BACKEND_URL` | Backend URL for OAuth callback | `http://localhost:8000` |

## 🎨 Screenshots

The application features:
- Modern, clean design with gradient accents
- Responsive layout for all devices
- Smooth animations and transitions
- Professional status badges and cards
- Intuitive search and filter controls

## 📄 License

MIT License - Feel free to use this project for learning and development.
