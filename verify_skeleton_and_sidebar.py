"""
Verification Test for Learn & Build Full-Page Skeleton and Sidebar Rename
"""

import unittest
from app import create_app

class TestSkeletonAndSidebar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def test_01_learn_and_build_skeleton_elements(self):
        """Verify Learn & Build page renders full-page layout-matched skeleton."""
        resp = self.client.get("/learning/courses")
        self.assertEqual(resp.status_code, 200)
        html = resp.data.decode("utf-8")

        # 1. Main skeleton container present
        self.assertIn('id="youtubeSkeleton"', html)
        self.assertIn('id="learnBuildSkeleton"', html)

        # 2. Hero Banner Skeleton present
        self.assertIn('class="learning-hero-card"', html)
        self.assertIn('sk-pill sk-dark', html)
        self.assertIn('sk-line sk-dark', html)

        # 3. Focus topics skeleton present
        self.assertIn('class="personalized-banner"', html)

        # 4. Filter chips & form skeleton present
        self.assertIn('class="bubble-filter-scroll"', html)
        self.assertIn('class="course-filter-grid"', html)

        # 5. Course card grid skeleton with 6 placeholder cards inside #learnBuildSkeleton
        skeleton_part = html.split('id="learnBuildSkeleton"')[1].split('{% elif')[0] if '{% elif' in html else html.split('id="learnBuildSkeleton"')[1].split('id="livePageContent"')[0]
        self.assertEqual(skeleton_part.count('course-card-custom'), 6)
        self.assertIn('sk-box sk-dark', html)

        # 6. Live content wrapper in loading state
        self.assertIn('id="livePageContent" class="live-content-wrapper is-loading"', html)

        # 7. NoScript fail-safe
        self.assertIn('<noscript>', html)
        self.assertIn('#youtubeSkeleton { display: none !important; }', html)

        # 8. Fail-safe inline reveal script present
        self.assertIn('Fail-safe immediate reveal', html)

    def test_02_sidebar_rename_to_skill_exchange(self):
        """Verify left sidebar navigation displays 'Skill Exchange' instead of 'Skill Exchange & Peers'."""
        # Check on public / unauthenticated page or authenticated
        resp = self.client.get("/discover")
        self.assertEqual(resp.status_code, 200)
        html = resp.data.decode("utf-8")

        # Header and title check
        self.assertIn("<title>Skill Exchange — Skill Rock</title>", html)
        self.assertIn("Skill Exchange", html)
        self.assertNotIn("Skill Exchange & Peers", html)

    def test_03_static_assets_configured(self):
        """Verify style.css and main.js handle the skeleton correctly."""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn(".sk-dark", css)
        self.assertIn(".live-content-wrapper.is-loading", css)
        self.assertIn("display: none !important;", css)

        with open("static/js/main.js", "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn('skeleton: document.getElementById("youtubeSkeleton")', js)
        self.assertIn('skeleton.style.display = "none"', js)
        self.assertIn('liveContent.classList.remove("is-loading")', js)


if __name__ == "__main__":
    unittest.main()
