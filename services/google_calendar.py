"""
SkillSwap Campus — Real Google Calendar & Google Meet Integration Service
Creates calendar events with real Google Meet links and 60-minute reminders.
Enforces idempotency to prevent duplicate calendar events.
"""

import os
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

def get_calendar_service_for_user(user):
    """
    Builds an authorized Google Calendar service resource for the user.
    Refreshes access token if expired and updates user record.
    Returns None if user has no Google OAuth tokens.
    """
    if not user or not user.google_access_token:
        return None

    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return None
    if "YOUR_GOOGLE" in client_id or "YOUR_GOOGLE" in client_secret:
        return None

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/calendar.events"]
    )

    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token to user document
            user.google_access_token = creds.token
            if creds.expiry:
                user.google_token_expiry = creds.expiry
            user.save()
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception as e:
        logger.warning(f"Could not build or refresh Google Calendar service for {user.email}: {e}")
        return None


def create_calendar_event_with_meet(session, current_user):
    """
    Creates a real Google Calendar event with a Google Meet link and 60-min reminder.
    
    Idempotent:
    - Checks if calendar_event_id is already present
    - Uses requestId based on session.id for the conference creation
    """
    if session.calendar_event_id and session.meeting_link:
        return {
            "success": True,
            "event_id": session.calendar_event_id,
            "meet_link": session.meeting_link,
            "cached": True
        }

    teacher = session.teacher
    learner = session.learner
    if not teacher or not learner:
        return {"success": False, "error": "Session participants not found", "meet_link": None}

    # Find which participant has authorized Google Calendar access
    organizer = None
    if current_user and current_user.google_access_token:
        organizer = current_user
    elif teacher.google_access_token:
        organizer = teacher
    elif learner.google_access_token:
        organizer = learner

    if not organizer:
        return {
            "success": False,
            "error": "Google Calendar authorization is required. Please sign in with Google or link your Google account to create calendar events and Google Meet links.",
            "meet_link": None
        }

    service = get_calendar_service_for_user(organizer)
    if not service:
        return {
            "success": False,
            "error": "Unable to initialize Google Calendar service. Please check Google OAuth credentials in .env.",
            "meet_link": None
        }

    try:
        # Build start and end datetime
        date_str = session.scheduled_date
        time_str = session.scheduled_time
        start_iso = f"{date_str}T{time_str}:00"
        start_dt = datetime.strptime(start_iso, "%Y-%m-%dT%H:%M:%S")
        end_dt = start_dt + timedelta(minutes=int(session.duration_minutes or 60))

        request_id = f"skillswap-session-{session.id}"

        event_body = {
            "summary": f"SkillSwap: {session.title}",
            "description": (
                f"SkillSwap Campus Peer Learning Session\n\n"
                f"Skill: {session.skill.name}\n"
                f"Teacher: {teacher.name} ({teacher.email})\n"
                f"Learner: {learner.name} ({learner.email})\n"
                f"Notes: {session.notes or 'No specific notes'}\n\n"
                f"Organized via SkillSwap Campus"
            ),
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "attendees": [
                {"email": teacher.email, "displayName": teacher.name},
                {"email": learner.email, "displayName": learner.name}
            ],
            # Google Meet Video Conference
            "conferenceData": {
                "createRequest": {
                    "requestId": request_id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            },
            # 60-Minute Reminders
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 60},
                    {"method": "email", "minutes": 60}
                ]
            }
        }

        # conferenceDataVersion=1 generates real Google Meet link
        created_event = service.events().insert(
            calendarId="primary",
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates="all"
        ).execute()

        event_id = created_event.get("id")
        meet_link = created_event.get("hangoutLink")
        if not meet_link:
            entry_points = created_event.get("conferenceData", {}).get("entryPoints", [])
            for ep in entry_points:
                if ep.get("entryPointType") == "video":
                    meet_link = ep.get("uri")
                    break

        # Save event details to session in MongoDB
        session.calendar_event_id = event_id
        session.meeting_link = meet_link or created_event.get("htmlLink") or ""
        session.calendar_event_data = {
            "event_id": event_id,
            "status": created_event.get("status"),
            "htmlLink": created_event.get("htmlLink"),
            "organizer": organizer.email,
            "reminder_minutes": 60
        }
        session.save()

        return {
            "success": True,
            "event_id": event_id,
            "meet_link": session.meeting_link,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Google Calendar event creation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "meet_link": None
        }


def cancel_calendar_event(session, current_user):
    """Cancels/deletes the Google Calendar event when a session is cancelled."""
    if not session.calendar_event_id:
        return False

    teacher = session.teacher
    learner = session.learner
    organizer = current_user if current_user.google_access_token else (teacher if teacher.google_access_token else learner)
    service = get_calendar_service_for_user(organizer)
    if not service:
        return False

    try:
        service.events().delete(calendarId="primary", eventId=session.calendar_event_id, sendUpdates="all").execute()
        return True
    except Exception as e:
        logger.warning(f"Could not cancel calendar event {session.calendar_event_id}: {e}")
        return False
