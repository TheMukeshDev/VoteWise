# VoteWise AI

**Your Smart Guide to Elections**

A civic-tech platform that bridges the gap between complex election processes and everyday voters through AI-powered guidance, multilingual support, and intuitive voter assistance.

---

## Overview

Voting is a fundamental right, yet many citizens—especially first-time voters—find the election process confusing. Between understanding registration requirements, finding polling locations, tracking important dates, and navigating language barriers, the path to casting an informed vote can feel overwhelming.

VoteWise AI addresses these challenges by providing a centralized, accessible platform where voters can learn about elections, get personalized guidance, and stay informed—all with the support of AI that speaks their language.

**Note:** This is an independent civic education platform. It does not facilitate actual voting, connect to government election systems, or have any affiliation with election commissions.

---

## The Problem

- **Registration complexity** — Many voters don't understand the registration process or miss deadlines
- **Information fragmentation** — Election information is scattered across multiple official websites
- **Language barriers** — Non-English speakers have limited access to election resources
- **First-time voter confusion** — New voters lack step-by-step guidance tailored to their needs
- **Location challenges** — Finding polling booths remains difficult for many citizens

---

## The Solution

VoteWise AI consolidates election education into a single, accessible platform. By combining AI-powered assistance with Google's robust infrastructure, we deliver:

- Instant answers to election questions in multiple languages
- Clear, structured guidance through the voting process
- Integrated polling booth discovery via Google Maps
- Calendar sync for registration deadlines and election day
- Voice input/output for users with varying literacy levels

---

## Features

### For Voters

- **AI Election Assistant** — Ask questions in natural language and receive structured, step-by-step answers
- **Election Timeline** — Track important dates from registration to results
- **Polling Booth Finder** — Locate your assigned polling station with directions
- **Smart Reminders** — Sync deadlines and election day to your Google Calendar
- **Multilingual Support** — Access guidance in Hindi, English, and regional languages
- **Voice Input** — Speak your questions instead of typing
- **First-Time Voter Guide** — Step-by-step guidance designed specifically for new voters

### For Administrators

- **Content Management** — Create and manage FAQs, timelines, and announcements
- **Polling Guidance Editor** — Add or update booth-specific information by state
- **User Analytics** — Monitor platform usage and query patterns
- **Announcements** — Push important updates to all users

---

## Product Modules

### Voter Dashboard

The main user interface where voters access all features:

- Quick action cards for common tasks
- Upcoming events timeline
- Reminder management
- AI chat interface
- Document checklist
- FAQ section

### Admin Dashboard

A secure management panel for content administrators:

- Overview with platform statistics
- FAQ CRUD operations
- Timeline event management
- Announcement creation
- Polling guidance by region
- User management view
- Usage analytics

### AI Chat Interface

A conversational interface powered by Google Gemini that:

- Accepts natural language questions
- Returns structured responses with steps and tips
- Provides actionable quick links
- Supports multiple languages
- Handles voice input

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Tailwind CSS, Vanilla JavaScript |
| **Backend** | Flask 2.3, Python 3.9+ |
| **Database** | Google Firestore (NoSQL) |
| **Authentication** | Firebase Auth |
| **AI** | Google Gemini API |
| **Maps** | Google Maps API |
| **Speech** | Google Cloud Speech-to-Text, Text-to-Speech |
| **Translation** | Google Translate API |
| **Calendar** | Google Calendar API |
| **Deployment** | Google Cloud Run |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Voter     │  │    Admin     │  │   Landing    │       │
│  │ Dashboard   │  │  Dashboard   │  │   Page       │       │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘       │
└─────────┼────────────────┼────────────────────────────────┘
          │                │
          └────────┬───────┘
                   │ REST API
          ┌────────▼─────────┐
          │   Flask Backend    │
          │                    │
          │  ┌──────────────┐ │
          │  │ API Routes   │ │
          │  │   (Blueprints)│ │
          │  └───────┬──────┘ │
          │          │        │
          │  ┌───────▼──────┐ │
          │  │   Services   │ │
          │  │   (Business  │ │
          │  │    Logic)    │ │
          │  └───────┬──────┘ │
          └──────────┼────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐    ┌───────────┐    ┌────────────┐
│Firestore│    │   Google  │    │   Gemini   │
│ Database│    │   APIs   │    │     AI     │
└─────────┘    └───────────┘    └────────────┘
```

### Backend Design

The Flask backend follows a layered architecture:

- **Routes** — Thin endpoints that handle HTTP requests
- **Services** — Business logic and API integrations
- **Middleware** — Authentication and error handling
- **Utils** — Response formatting and validation

### Frontend Design

The frontend uses a component-based structure:

- Responsive layouts with Tailwind CSS
- State management via vanilla JavaScript
- Reusable component patterns
- Consistent design system with CSS variables

---

## User Roles

### Voter

Default role for all authenticated users. Voters can:

- Chat with the AI assistant
- View election timeline
- Find polling booths
- Set reminders
- Browse FAQs
- Manage their profile

### Admin

Elevated role for content management. Admins can:

- All voter capabilities
- Create, edit, and delete FAQs
- Manage election timeline events
- Publish announcements
- Edit polling guidance by region
- View platform analytics

Admin access is assigned manually and cannot be self-provisioned through the application.

---

## Google Services Integration

| Service | Integration Purpose |
|---------|---------------------|
| **Firestore** | Persistent storage for user profiles, FAQs, timelines, reminders |
| **Firebase Auth** | Secure user authentication via email/password and Google sign-in |
| **Maps API** | Polling booth location search and directions |
| **Calendar API** | ICS file generation for reminder sync |
| **Translate API** | Multilingual support for all content |
| **Speech-to-Text** | Voice input for chat interface |
| **Text-to-Speech** | Voice output for responses |
| **Gemini API** | Natural language understanding and response generation |
| **Cloud Run** | Containerized backend deployment |

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher (for frontend build)
- Google Cloud account with billing enabled
- Firebase project with Authentication and Firestore

### Backend Setup

1. Clone the repository and navigate to the project directory

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with required variables:
   ```env
   SECRET_KEY=your-secure-random-key
   FLASK_ENV=development
   FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   GEMINI_API_KEY=your-gemini-key
   GOOGLE_MAPS_API_KEY=your-maps-key
   ```

5. Run the development server:
   ```bash
   python app.py
   ```

### Frontend Setup

The frontend templates are served directly by Flask. For development with hot-reload:

1. Serve the `templates` directory with your preferred static file server
2. Update API endpoints in `static/js/app.js` if needed
3. Use Tailwind CLI for CSS development:
   ```bash
   npx tailwindcss -i ./static/css/input.css -o ./static/css/style.css --watch
   ```

### Testing

Run the backend test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

---

## Folder Structure

```
VoteWise/
├── app.py                 # Application factory and entry point
├── config.py              # Environment-based configuration
├── requirements.txt       # Python dependencies
│
├── routes/                # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── chat.py           # AI chat endpoint
│   ├── election.py       # Election data endpoints
│   ├── faq.py            # FAQ management
│   ├── timeline.py      # Timeline management
│   ├── reminder.py       # Calendar reminder generation
│   ├── polling.py        # Polling booth search
│   └── user.py           # User profile operations
│
├── services/             # Business logic layer
│   ├── auth_service.py   # Firebase authentication
│   ├── firestore_service.py # Database operations
│   ├── google_services_hub.py # Google API orchestration
│   ├── maps_service.py   # Google Maps integration
│   ├── calendar_service.py # Calendar/ICS generation
│   ├── translate_service.py # Translation API wrapper
│   └── analytics_service.py # Usage logging
│
├── middleware/           # Request processing
│   ├── auth_middleware.py # JWT verification and role checks
│   └── error_handler.py  # Global exception handling
│
├── utils/                # Helper functions
│   ├── response.py       # Standardized API responses
│   ├── validators.py     # Input validation
│   └── logging_config.py # Structured logging
│
├── templates/            # Frontend HTML
│   ├── index.html        # Landing page
│   ├── app.html         # Voter dashboard
│   ├── admin.html       # Admin panel
│   ├── login.html       # Sign-in page
│   ├── signup.html      # Registration page
│   ├── profile.html     # User profile page
│   └── settings.html     # User settings page
│
├── static/
│   ├── css/
│   │   └── style.css    # Compiled Tailwind styles
│   └── js/
│       └── app.js       # Frontend JavaScript
│
└── tests/                # Test suite
    ├── conftest.py      # Test fixtures
    ├── test_auth.py     # Authentication tests
    ├── test_chat.py     # Chat endpoint tests
    ├── test_faqs.py     # FAQ management tests
    ├── test_reminders.py # Reminder tests
    └── test_smoke.py    # Page load tests
```

---

## API Overview

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Authenticate with Firebase token |
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/google-signin` | Sign in with Google |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/profile` | Update profile fields |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/chat` | Send message to AI assistant |

### Content

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/faqs` | List all FAQs |
| GET | `/api/timeline` | Get election timeline |
| GET | `/api/election/process` | Get election process guide |
| POST | `/api/reminders` | Generate ICS reminder file |

### Admin (Protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/faqs` | Create new FAQ |
| PUT | `/api/faqs/<id>` | Update FAQ |
| DELETE | `/api/faqs/<id>` | Delete FAQ |

All API responses follow a standardized format:

```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "errors": { "field": "Validation message" }
}
```

---

## Security

- **Token-based authentication** — Firebase ID tokens verified server-side
- **JWT access tokens** — Short-lived tokens for API authorization
- **Role-based access control** — Admin routes protected by role middleware
- **Input validation** — All user input sanitized before processing
- **Secure error messages** — Internal details never exposed to clients
- **User data isolation** — Users can only access their own reminders and profile
- **CORS configuration** — Configurable origin restrictions

### What We Don't Do

- We don't store passwords (Firebase handles auth)
- We don't expose API keys client-side
- We don't allow role self-assignment
- We don't log sensitive user data
- We don't connect to government systems

---

## Accessibility

- Semantic HTML elements throughout
- ARIA labels on interactive elements
- Keyboard navigation support
- Visible focus indicators
- High contrast dark theme
- Touch-friendly button sizes
- Screen reader compatible navigation

---

## Future Improvements

- **Mobile application** — Native iOS and Android apps
- **Push notifications** — Web push for reminders
- **Offline support** — PWA with cached content
- **Community FAQs** — User-contributed Q&A with moderation
- **Voter verification** — Integration with election commission APIs (where available)
- **Election day features** — Real-time queue length estimates at polling stations
- **Multi-country support** — Adaptable election education framework

---

## Disclaimer

VoteWise AI is an independent civic education platform created to help citizens understand election processes. It is:

- **Not affiliated** with any government election commission
- **Not a voting portal** — Cannot be used to cast votes
- **Not official** — Does not connect to government systems
- **Educational only** — All information should be verified through official sources

The platform does not store, process, or transmit any vote data. For authoritative election information, always refer to your local election commission's official website.

---

## Author

Built with purpose for civic empowerment.

For questions, feedback, or collaboration opportunities, open an issue on this repository.

---

## License

This project is available for educational and non-commercial use. See LICENSE file for details.