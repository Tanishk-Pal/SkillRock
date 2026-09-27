# SkillSwap Campus — Production Setup Checklist

Use this checklist to verify that all production services are configured and running correctly.

---

## 🚀 Quick Setup Status

| Service | Component | Status | Required Action |
| :--- | :--- | :---: | :--- |
| **Database** | MongoDB Database | ⚙️ Configurable | Provide `MONGODB_URI` in `.env` (or local fallback) |
| **Auth** | Campus Email / Password | ✅ Ready | Works immediately out-of-the-box |
| **OAuth** | Google 1-Click Login | ⚙️ Configurable | Follow `GOOGLE_SETUP.md` |
| **Calendar** | Google Calendar + Google Meet | ⚙️ Configurable | Follow `GOOGLE_SETUP.md` |
| **AI** | SkillBot Gemini 2.5 Flash | ⚙️ Configurable | Provide `GEMINI_API_KEY` in `.env` |
| **Matching** | 70/45/30 Matching Algorithm | ✅ Ready | Works automatically with student skills |
| **Gamification**| XP, Levels, Badges Engine | ✅ Ready | Works automatically on student actions |

---

## 📋 Step-by-Step Production Checklist

### 1. Database Configuration (MongoDB)
- [ ] **Create MongoDB Database**
  - Option A: Free [MongoDB Atlas Cluster](https://www.mongodb.com/cloud/atlas) (Recommended for cloud/production)
  - Option B: Local MongoDB instance (`mongodb://127.0.0.1:27017/skillswap_campus`)
- [ ] Set `MONGODB_URI` in `.env`:
  ```ini
  MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority
  MONGODB_DB_NAME=skillswap_campus
  ```
- [ ] Initialize standard database collections and system badges:
  ```powershell
  python init_db.py
  ```

---

### 2. Application Security
- [ ] Generate a secure, unique `SECRET_KEY` for Flask session signing:
  ```powershell
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Set `SECRET_KEY` in `.env`:
  ```ini
  SECRET_KEY=your_generated_hex_secret_key
  ```

---

### 3. Google OAuth 2.0 & Google Meet Video Calls
- [ ] Open [Google Cloud Console](https://console.cloud.google.com/) and create a project (`SkillSwap Campus`).
- [ ] Enable **Google Calendar API** in API Library.
- [ ] Configure **OAuth Consent Screen**:
  - Scopes: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/calendar.events`
  - Add your developer and test emails to **Test Users**.
- [ ] Create **OAuth 2.0 Web Client Credentials**:
  - Authorized Origins: `http://127.0.0.1:5000`, `http://localhost:5000`
  - Authorized Redirect URIs: `http://127.0.0.1:5000/auth/google/callback`, `http://localhost:5000/auth/google/callback`
- [ ] Copy credentials to `.env`:
  ```ini
  GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=GOCSPX-your_client_secret
  GOOGLE_REDIRECT_URI=http://127.0.0.1:5000/auth/google/callback
  ```
- [ ] Read [GOOGLE_SETUP.md](GOOGLE_SETUP.md) for detailed screenshots and troubleshooting.

---

### 4. Gemini AI Integration (SkillBot)
- [ ] Visit [Google AI Studio](https://aistudio.google.com/) and generate a free Gemini API key.
- [ ] Set `GEMINI_API_KEY` in `.env`:
  ```ini
  GEMINI_API_KEY=your_gemini_api_key_here
  ```
- [ ] Test live AI chat on `http://127.0.0.1:5000/assistant`.

---

### 5. Verification & Testing
- [ ] Run the automated 18-step production verification suite:
  ```powershell
  python verify_e2e_production.py
  ```
  *(Expected result: "🎉 ALL 18 PRODUCTION E2E VERIFICATION CHECKS PASSED 100%!")*

- [ ] Start the development server:
  ```powershell
  python app.py
  ```

- [ ] Open in browser: `http://127.0.0.1:5000`
