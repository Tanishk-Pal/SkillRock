# 🎓 SkillSwap Campus
> **Learn. Teach. Grow Together.** — Real-world Student Skill Exchange Web Platform

SkillSwap Campus is a production-ready web platform where college students **teach skills they know and learn skills they want** from their peers.

Built with **Flask**, **MongoDB**, **Google OAuth 2.0**, **Google Calendar API + Google Meet**, and the **Google Gemini API**.

---

## 🌟 Highlights of the Real Production Architecture

- **Zero Fake / Demo Data**: All users, skills, swap requests, connections, sessions, and ratings are stored in real database collections. Empty states guide students naturally.
- **MongoDB Data Layer**: Fully indexed collections with duplicate-action prevention on email, mutual swap requests, connections, session times, and ratings.
- **Real Google OAuth 2.0**: One-click Google login (`/auth/google`) using your official college or Google account. Fetches Google profile photo and initializes student profile safely.
- **Real Google Calendar & Google Meet Integration**: When a session is scheduled, it generates a real Google Calendar event with a **Google Meet video call link** (`conferenceDataVersion=1`) and automated 60-minute email and popup reminders.
- **Real Google Gemini AI (`gemini-2.5-flash`)**: Live SkillBot answering skill questions and generating custom learning roadmaps. Honest configuration prompts when keys are not yet configured.
- **Transparent Skill Matching Algorithm**:
  - Direct Mutual Match: 70 points
  - One-Way Match: 45 points
  - Related Skill: 30 points
  - Same College: +10 points
  - Same Branch: +5 points
  - Same Year: +5 points
  - Maximum Score: 100%
- **Campus Gamification Engine**:
  - Swap Request Accepted: +20 XP to both students
  - Teach Session Completed: +20 XP to teacher
  - Learn Session Completed: +10 XP to learner
  - 5-Star Rating Received: +5 XP bonus
  - Tiered Levels: Beginner (0–99), Learner (100–249), Skill Builder (250–499), Knowledge Sharer (500–999), Skill Mentor (1000+)
  - System Badges: *First Swap*, *Knowledge Sharer*, *Fast Learner*, *Community Builder*, *Skill Mentor*
- **SaaS Light Design System**: Clean, modern interface with dark navy headers, bright blue actions, crisp white cards, Lucide icons, and zero cluttered text.

---

## 🏗️ Project Structure

```text
skillswap-campus/
├── app.py                      # Flask application factory, routes, and error handlers
├── config.py                   # Environment, MongoDB, and OAuth configuration
├── init_db.py                  # Initializes MongoDB collections, indexes, and standard skills
├── verify_e2e_production.py    # 18-step end-to-end automated production test suite
├── requirements.txt            # Python dependencies
├── .env.example                # Production environment variable template
├── .env                        # Local configuration file (gitignored)
├── GOOGLE_SETUP.md             # Step-by-step Google Cloud Console setup guide
├── SETUP_CHECKLIST.md          # Verification checklist for all cloud services
├── README.md                   # Complete documentation
│
├── models/                     # MongoDB models and data layer
│   ├── __init__.py             # Exports User, Skill, SwapRequest, Connection, Session, etc.
│   └── mongo.py                # MongoDB collections, indexes, and methods
│
├── routes/                     # Blueprint route handlers
│   ├── __init__.py             # Blueprint registration
│   ├── auth.py                 # Real Google OAuth 2.0 & Campus Email/Password auth
│   ├── dashboard.py            # Overview, stats, and upcoming sessions
│   ├── discover.py             # Peer discovery with skill filters and matching scores
│   ├── profile.py              # Profile management and skill additions/removals
│   ├── swap.py                 # Swap requests lifecycle with authorization guards
│   ├── connections.py          # Active peer connections hub
│   ├── sessions.py             # Session scheduling, Google Calendar, completion & ratings
│   └── ai.py                   # SkillBot AI chat and learning roadmap generator
│
├── services/                   # Business logic and external integrations
│   ├── ai_service.py           # Google GenAI (gemini-2.5-flash) client
│   ├── google_auth.py          # Google OAuth 2.0 authorization code flow
│   ├── google_calendar.py      # Google Calendar API & Google Meet generation
│   ├── matching.py             # 70/45/30 skill matching calculation engine
│   └── xp_service.py           # XP awarding and badge unlocking
│
├── static/                     # Static assets
│   ├── css/style.css           # Clean SaaS light design system
│   └── js/main.js              # Client-side helpers and interactive modal logic
│
└── templates/                  # Jinja2 HTML templates
    ├── base.html               # Base layout, navigation, flash alerts, and modal
    ├── index.html              # Landing page
    ├── login.html              # Login page with Google OAuth button
    ├── register.html           # Campus registration page
    ├── dashboard.html          # Student dashboard
    ├── discover.html           # Peer discovery directory
    ├── profile.html            # Profile, skills, and badge portfolio
    ├── edit_profile.html       # Profile editor
    ├── requests.html           # Pending and sent swap requests
    ├── connections.html        # Active student connections
    ├── sessions.html           # Scheduled and past sessions with Meet links
    ├── rate_session.html       # Post-session star rating and feedback form
    └── assistant.html          # SkillBot AI assistant chat interface
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- (Optional) MongoDB Atlas free account or local MongoDB instance
- (Optional) Google Cloud Console project for Google Sign In & Calendar
- (Optional) Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation

```powershell
# Clone or navigate to the project directory
cd "skillswap-campus"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables Configuration

Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

Open `.env` and configure your settings:
```ini
# Flask Secret Key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=replace_with_your_secure_hex_secret_key

# MongoDB Connection
# Set to your MongoDB Atlas connection string (or leave empty for testing):
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=skillswap_campus

# Google Cloud OAuth 2.0 (See GOOGLE_SETUP.md)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_client_secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:5000/auth/google/callback

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Initialize Database

Run the database initializer to create collections, indexes, and standard skills:
```powershell
python init_db.py
```

### 5. Run Production Verification Suite

Verify all 18 end-to-end integration and security checks:
```powershell
python verify_e2e_production.py
```
Expected output:
```text
🎉 ALL 18 PRODUCTION E2E VERIFICATION CHECKS PASSED 100%!
```

### 6. Start the Server

```powershell
python app.py
```

Open your browser at:
`http://127.0.0.1:5000`

---

## 📖 Setup Guides

- **[GOOGLE_SETUP.md](GOOGLE_SETUP.md)**: Complete step-by-step instructions for Google Cloud Console, Google OAuth Consent Screen, Google Calendar API, and Google Meet link generation.
- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)**: Quick-reference checklist to track the status of all integrations.

---

## 🔒 Security Architecture

- **Password Hashing**: PBKDF2 with SHA-256 via Werkzeug security.
- **Server-Side Authorization**: Every swap request, connection, session completion, and rating is verified server-side against `current_user.id`.
- **Duplicate Protection**:
  - Unique index on user email.
  - Unique compound index on swap requests (`sender_id` + `receiver_id` + `status="pending"`).
  - Canonical order on connections (`user1_id < user2_id`).
  - Session scheduling collision guard (`connection_id` + `scheduled_date` + `scheduled_time`).
  - Single-review per session guard (`session_id` + `reviewer_id`).
  - Duplicate XP prevention flags (`xp_awarded = True`).
