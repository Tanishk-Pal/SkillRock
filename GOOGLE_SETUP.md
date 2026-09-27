# Google Cloud Setup Guide — SkillSwap Campus

This guide walks you through setting up **Real Google OAuth 2.0 Login** and **Real Google Calendar + Google Meet Video Call Scheduling** for SkillSwap Campus.

> **IMPORTANT**: All steps in this document require access to your Google Cloud Console. Any section tagged with **`[MANUAL STEP — USER MUST DO THIS]`** requires your action.

---

## 📋 Overview of What We Are Setting Up

1. **Google OAuth 2.0**: Allows students to log in using their college or personal Google account.
2. **Google Calendar API**: Automatically schedules peer learning sessions on both students' Google Calendars.
3. **Google Meet Conference**: Creates a real Google Meet video call room for the scheduled session with 60-minute email and popup reminders.

---

## Step 1: Create a Google Cloud Project
**`[MANUAL STEP — USER MUST DO THIS]`**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your Google account.
3. Click the **Project Selector** dropdown at the top of the page.
4. Click **New Project**.
5. Set:
   - **Project Name**: `SkillSwap Campus` (or any name you prefer)
   - **Location**: Leave default (*No organization*)
6. Click **Create** and wait a few seconds for the project to provision.
7. Select the new project from the top dropdown.

---

## Step 2: Enable Required APIs
**`[MANUAL STEP — USER MUST DO THIS]`**

1. In the Google Cloud Console navigation menu (top-left burger menu ☰), go to **APIs & Services** > **Library**.
2. Search for: `Google Calendar API`.
3. Click **Google Calendar API** from the results.
4. Click the blue **Enable** button.
5. (Optional but recommended) In the API Library, search for `Google People API` and verify it is enabled.

---

## Step 3: Configure the OAuth Consent Screen
**`[MANUAL STEP — USER MUST DO THIS]`**

1. In the left sidebar, navigate to **APIs & Services** > **OAuth consent screen**.
2. Under **User Type**, select **External** (unless you are using Google Workspace for your college, in which case select *Internal*).
3. Click **Create**.
4. Fill in the **App Information**:
   - **App name**: `SkillSwap Campus`
   - **User support email**: Select your email address
   - **Developer contact information**: Enter your email address
5. Click **Save and Continue**.
6. On the **Scopes** page, click **Add or Remove Scopes**:
   - Select: `userinfo.email` (`.../auth/userinfo.email`)
   - Select: `userinfo.profile` (`.../auth/userinfo.profile`)
   - Select: `openid`
   - Scroll down to *Manually add scopes* and paste:
     ```
     https://www.googleapis.com/auth/calendar.events
     ```
   - Click **Add to Table**, then click **Update**.
7. Click **Save and Continue**.
8. On the **Test Users** page (critical while app is in *Testing* status):
   - Click **+ Add Users**.
   - Enter your email address and any test student email addresses you plan to test with.
   - Click **Add**.
9. Click **Save and Continue**, then return to the Dashboard.

---

## Step 4: Create OAuth 2.0 Credentials
**`[MANUAL STEP — USER MUST DO THIS]`**

1. In the left sidebar, click **Credentials**.
2. At the top, click **+ Create Credentials** > **OAuth client ID**.
3. In the **Application type** dropdown, select **Web application**.
4. Set:
   - **Name**: `SkillSwap Web Client`
5. Under **Authorized JavaScript origins**, click **+ Add URI** and add:
   - `http://127.0.0.1:5000`
   - `http://localhost:5000`
6. Under **Authorized redirect URIs**, click **+ Add URI** and add:
   - `http://127.0.0.1:5000/auth/google/callback`
   - `http://localhost:5000/auth/google/callback`
7. Click **Create**.
8. A modal dialog will appear showing:
   - **Your Client ID** (e.g., `123456789012-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com`)
   - **Your Client Secret** (e.g., `GOCSPX-abcdefghijklmnopqrstuvwxyz`)
9. Copy both values. **Never commit your Client Secret to git.**

---

## Step 5: Configure SkillSwap Campus `.env` File
**`[MANUAL STEP — USER MUST DO THIS]`**

Open your project root `.env` file (e.g. `C:\Users\Tanishk Pal\OneDrive\Desktop\skillswap-campus\.env`) and set the following variables:

```ini
# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_client_secret_here
GOOGLE_REDIRECT_URI=http://127.0.0.1:5000/auth/google/callback
```

Save the file.

---

## Step 6: Verify Google Login & Meet Generation

1. Start the Flask application:
   ```powershell
   python app.py
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/login
   ```
3. Click **Continue with Google**.
4. Sign in with your Google account (ensure it was added to *Test Users* in Step 3).
5. Grant permissions to view profile and manage Google Calendar events.
6. Once logged in:
   - Connect with another student.
   - Schedule a session.
   - Both you and your peer will receive Google Calendar event invitations with a clickable **Google Meet Video Call** link and automated reminders set for 60 minutes before the call!

---

## 🔒 Security Best Practices

- Keep `GOOGLE_CLIENT_SECRET` private. Never paste it in chat, screenshots, or push it to public repositories.
- Keep `.env` in your `.gitignore` file.
- When deploying to production (e.g. Render, Railway, AWS), add your production HTTPS domain to **Authorized JavaScript origins** and **Authorized redirect URIs** in Google Cloud Console.
