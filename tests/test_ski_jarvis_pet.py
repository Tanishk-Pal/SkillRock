import os
os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"
import unittest
from flask import json
from app import create_app
from services.ai_service import (
    chat_with_ski,
    resolve_jarvis_local_intent,
    synthesize_local_jarvis_response,
    get_local_skillrock_catalogue
)


class TestSkiJarvisPet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def test_local_skillrock_catalogue(self):
        """Verifies that local catalogue contains AI, Full Stack, Roadmap, and Bhavishya entries."""
        cat = get_local_skillrock_catalogue()
        self.assertGreaterEqual(len(cat), 10)
        
        # Check AI course exists
        ai_course = next((c for c in cat if c["id"] == "ai-ml-python"), None)
        self.assertIsNotNone(ai_course)
        self.assertEqual(ai_course["url"], "/learning/course/machine-learning-ai-python")

    def test_ski_ai_course_intent_and_reply(self):
        """
        Verifies requirement:
        User asks: 'Ski I want a super course on AI'
        Ski replies: 'Yes (Name of User) I have a good AI course for you: ...'
        and provides exact redirect_url and navigate action.
        """
        user_name = "Tanishk"
        query = "Ski I want a super course on AI"
        res = chat_with_ski(query, user_context={"name": user_name})

        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "navigate")
        self.assertEqual(res["redirect_url"], "/learning/course/machine-learning-ai-python")
        
        # Check reply string matches exact user specification
        self.assertIn(f"Yes {user_name}, I have a good AI course for you", res["reply"])
        self.assertIn("Machine Learning & AI with Python", res["reply"])
        
        # Check thinking steps are present
        self.assertIn("thinking_steps", res)
        self.assertGreaterEqual(len(res["thinking_steps"]), 3)

    def test_ski_fullstack_roadmap_intent(self):
        """Verifies roadmap navigation via Ski."""
        res = chat_with_ski("I want the full stack roadmap", user_context={"name": "Aarav"})
        self.assertEqual(res["action"], "navigate")
        self.assertEqual(res["redirect_url"], "/roadmaps/full-stack-developer-launchpad")

    def test_ski_instant_local_conversations(self):
        """Verifies greetings, identity and humor respond instantly without external delays."""
        res_id = chat_with_ski("Who are you?", user_context={"name": "Priya"})
        self.assertIn("Ski", res_id["reply"])
        self.assertIn("Jarvis", res_id["reply"])

        res_hi = chat_with_ski("Hi Ski", user_context={"name": "Priya"})
        self.assertIn("Priya", res_hi["reply"])

        res_joke = chat_with_ski("Tell me a dev joke", user_context={"name": "Priya"})
        self.assertTrue(len(res_joke["reply"]) > 10)

    def test_api_ski_chat_endpoint(self):
        """Verifies HTTP POST /api/ski/chat returns properly formatted JSON with all Jarvis attributes."""
        payload = {
            "message": "Ski I want a super course on AI",
            "mood": "grok",
            "current_url": "/dashboard"
        }
        res = self.client.post("/api/ski/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("action"), "navigate")
        self.assertEqual(data.get("redirect_url"), "/learning/course/machine-learning-ai-python")
        self.assertIn("thinking_steps", data)
        self.assertEqual(data.get("bot_name"), "Ski")

    def test_sidebar_skillbot_removed_and_ski_assistant_present(self):
        """Verifies SkillBot AI tab is removed and Ski Assistant tab is active in base template."""
        with open("templates/base.html", "r", encoding="utf-8") as f:
            content = f.read()

        # SkillBot AI link must be gone from the sidebar
        self.assertNotIn("<span>SkillBot AI</span>", content)
        # Ski Assistant link with JARVIS badge must be present
        self.assertIn("<span>Ski Assistant</span>", content)
        self.assertIn("JARVIS", content)

    def test_ski_cute_hinglish_voice_and_autonomous_features(self):
        """Verifies cute child Hinglish persona, autonomous roaming and wake word in templates."""
        with open("templates/includes/ski_floating_widget.html", "r", encoding="utf-8") as f:
            widget_content = f.read()

        # Check wake-word recognition hook
        self.assertIn("wake-word", widget_content.lower())
        self.assertIn("speechrecognition", widget_content.lower())
        self.assertIn("ski", widget_content.lower())
        self.assertIn("skillrock", widget_content.lower())

        # Check autonomous roaming engine
        self.assertIn("roamautonomously", widget_content.lower())
        self.assertIn("walking", widget_content.lower())

        # Check cute 5-year-old high pitch
        self.assertIn("1.72", widget_content)


if __name__ == "__main__":
    unittest.main()
