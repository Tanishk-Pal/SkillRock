# -*- coding: utf-8 -*-
"""
Unit tests for Google OAuth Dynamic Redirect URI, Graceful Error Handling,
and Frontpage Hero Google / Sign In Buttons.
"""

import os
import unittest
from unittest import mock
from urllib.parse import urlparse, parse_qs
from app import create_app

class TestGoogleAuthAndFrontpage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure test Google OAuth environment
        os.environ["GOOGLE_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"
        os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret-12345"
        os.environ["GOOGLE_REDIRECT_URI"] = ""
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def test_01_frontpage_renders_google_and_signin_buttons(self):
        """Frontpage hero should have 'Continue with Google' and 'Sign In' buttons for unauthenticated visitors."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Continue with Google", html)
        self.assertIn("hero-btn-google", html)
        self.assertIn("hero-btn-signin", html)
        self.assertIn("Sign In", html)
        self.assertIn("/auth/google", html)
        self.assertIn("/login", html)

    def test_02_google_login_on_render_domain(self):
        """Visiting /auth/google on skillrock.onrender.com should redirect to Google OAuth with onrender callback URI."""
        response = self.client.get(
            "/auth/google",
            headers={"Host": "skillrock.onrender.com", "X-Forwarded-Proto": "https"}
        )
        self.assertEqual(response.status_code, 302)
        location = response.headers.get("Location", "")
        self.assertTrue(location.startswith("https://accounts.google.com/o/oauth2/auth"))
        parsed = urlparse(location)
        qs = parse_qs(parsed.query)
        self.assertEqual(qs.get("redirect_uri"), ["https://skillrock.onrender.com/auth/google/callback"])

    def test_03_google_login_on_custom_domain(self):
        """Visiting /auth/google on skillrock.in should use the authorized callback and sign the origin in state."""
        response = self.client.get(
            "/auth/google",
            headers={"Host": "skillrock.in", "X-Forwarded-Proto": "https"}
        )
        self.assertEqual(response.status_code, 302)
        location = response.headers.get("Location", "")
        self.assertTrue(location.startswith("https://accounts.google.com/o/oauth2/auth"))
        parsed = urlparse(location)
        qs = parse_qs(parsed.query)
        self.assertEqual(qs.get("redirect_uri"), ["https://skillrock.onrender.com/auth/google/callback"])
        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(self.app.config["SECRET_KEY"], salt="skillrock-auth-bridge")
        state_data = s.loads(qs.get("state")[0], max_age=600)
        self.assertEqual(state_data.get("origin"), "https://skillrock.in")

    def test_04_google_login_on_local_host(self):
        """Visiting /auth/google on localhost/127.0.0.1 should use http://{host}/auth/google/callback."""
        response = self.client.get(
            "/auth/google",
            headers={"Host": "127.0.0.1:5000"}
        )
        self.assertEqual(response.status_code, 302)
        location = response.headers.get("Location", "")
        parsed = urlparse(location)
        qs = parse_qs(parsed.query)
        self.assertEqual(qs.get("redirect_uri"), ["http://127.0.0.1:5000/auth/google/callback"])

    def test_05_never_returns_500_even_if_oauth_fails(self):
        """If Google OAuth flow fails unexpectedly, it should gracefully redirect to /login rather than 500."""
        with mock.patch("routes.auth.get_google_auth_flow", side_effect=Exception("OAuth Provider Network Glitch")):
            response = self.client.get("/auth/google", headers={"Host": "skillrock.onrender.com"})
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.headers.get("Location", ""))

    def test_06_bridge_login_valid_token(self):
        """Bridge login should authenticate user with a signed one-time token."""
        from itsdangerous import URLSafeTimedSerializer
        from models import User
        with self.app.app_context():
            users = User.find_all(limit=1)
            user = users[0] if users else User.create(email="bridge.test@skillrock.in", name="Bridge Test")
            s = URLSafeTimedSerializer(self.app.config["SECRET_KEY"], salt="skillrock-auth-bridge")
            token = s.dumps({"user_id": str(user.id), "next": "/learning/courses"})

        response = self.client.get(f"/auth/bridge-login?token={token}")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/learning/courses", response.headers.get("Location", ""))

    def test_07_bridge_login_invalid_token(self):
        """Bridge login should safely redirect to /login if token is invalid or corrupted."""
        response = self.client.get("/auth/bridge-login?token=invalid.tampered.token")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers.get("Location", ""))

if __name__ == "__main__":
    unittest.main()
