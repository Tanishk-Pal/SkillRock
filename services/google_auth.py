"""
SkillSwap Campus — Real Google OAuth 2.0 Service
Handles OAuth 2.0 flow for Google Login, user profile extraction,
and requesting Google Calendar scopes for scheduling sessions.
"""

import os
import logging
import requests

# Enable HTTP and relaxed scope matching for local Google OAuth development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

from google_auth_oauthlib.flow import Flow

logger = logging.getLogger(__name__)

# Required Google Scopes for Login & Calendar Scheduling
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events"
]

def is_google_auth_configured():
    """Checks whether real Google OAuth credentials have been provided in .env."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return False
    if "YOUR_GOOGLE" in client_id or "YOUR_GOOGLE" in client_secret:
        return False
    return True

def get_google_auth_flow(redirect_uri, state=None):
    """
    Creates and returns a Google OAuth Flow instance configured with scopes.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }

    # Allow HTTP and relaxed scope matching in local development
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
        state=state,
        autogenerate_code_verifier=False
    )
    return flow

def fetch_google_user_profile(access_token):
    """Fetches user profile information from Google UserInfo endpoint."""
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    res = requests.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=8)
    if res.status_code == 200:
        return res.json()
    else:
        logger.error(f"Failed to fetch userinfo from Google: {res.status_code} {res.text}")
        return None
