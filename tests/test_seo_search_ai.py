"""
SkillRock — Automated SEO, Search Engine & AI Discoverability Test Suite
Validates canonical URLs, robots directives, XML sitemap purity, llms.txt endpoints,
structured data (JSON-LD), 301 trailing slash normalization, and social sharing cards.
"""

import unittest
from app import create_app
from config import Config

class TestSEOSearchAIDiscoverability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class TestConfig(Config):
            TESTING = True
            WTF_CSRF_ENABLED = False
            SERVER_NAME = "localhost"

        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()

    def test_google_site_verification(self):
        """Verify the Google Search Console verification token endpoint is served correctly."""
        res = self.client.get("/google26078168ee5d1f7d.html")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)
        self.assertEqual(res.data.decode("utf-8").strip(), "google-site-verification: google26078168ee5d1f7d.html")

    def test_robots_txt(self):
        """Verify robots.txt allows public crawlable paths, blocks private paths, and references canonical sitemap."""
        res = self.client.get("/robots.txt")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/plain", res.content_type)
        content = res.data.decode("utf-8")
        
        # Verify allowed paths
        self.assertIn("Allow: /", content)
        self.assertIn("Allow: /learning/courses", content)
        self.assertIn("Allow: /static/", content)
        self.assertIn("Allow: /llms.txt", content)
        self.assertIn("Allow: /llms-full.txt", content)

        # Verify protected paths
        self.assertIn("Disallow: /admin/", content)
        self.assertIn("Disallow: /chat/", content)
        self.assertIn("Disallow: /messages/", content)
        self.assertIn("Disallow: /settings/", content)
        self.assertIn("Disallow: /api/", content)
        self.assertIn("Disallow: /login", content)
        self.assertIn("Disallow: /register", content)

        # Verify canonical sitemap reference
        self.assertIn("Sitemap: https://skillrock.onrender.com/sitemap.xml", content)

    def test_sitemap_xml(self):
        """Verify sitemap.xml uses HTTPS canonical domain, excludes private/imaginary routes, and includes courses."""
        res = self.client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/xml", res.content_type)
        content = res.data.decode("utf-8")

        # Verify XML structure
        self.assertIn('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', content)
        self.assertIn("<loc>https://skillrock.onrender.com/</loc>", content)
        self.assertIn("<loc>https://skillrock.onrender.com/learning/courses</loc>", content)

        # Verify private/auth/imaginary routes are EXCLUDED
        self.assertNotIn("/login", content)
        self.assertNotIn("/register", content)
        self.assertNotIn("/admin", content)
        self.assertNotIn("/dashboard", content)
        self.assertNotIn("/ai-assistant", content)

    def test_llms_txt(self):
        """Verify llms.txt is accessible, formatted as markdown, and documents public courses."""
        res = self.client.get("/llms.txt")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn("# SkillRock", content)
        self.assertIn("https://skillrock.onrender.com", content)
        self.assertIn("https://skillrock.onrender.com/learning/courses", content)
        self.assertIn("Project-Based", content)
        self.assertIn("Quiz-Based", content)

    def test_llms_full_txt(self):
        """Verify llms-full.txt provides the extended curriculum syllabus directory."""
        res = self.client.get("/llms-full.txt")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn("# SkillRock — Full Curriculum", content)
        self.assertIn("https://skillrock.onrender.com/learning/courses/", content)

    def test_trailing_slash_301_redirect(self):
        """Verify non-root trailing slashes return 301 permanent redirect to non-trailing slash version."""
        res = self.client.get("/learning/courses/")
        self.assertEqual(res.status_code, 301)
        self.assertEqual(res.location, "/learning/courses")

    def test_homepage_seo_elements(self):
        """Verify homepage has canonical link, single H1, OG tags, and schema markup."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")

        # Canonical tag
        self.assertIn('<link rel="canonical" href="https://skillrock.onrender.com/">', content)
        
        # Robots tag
        self.assertIn('content="index, follow', content)

        # Single H1 tag
        self.assertEqual(content.count("<h1"), 1)

        # Open Graph Banner 1200x630
        self.assertIn('property="og:image" content="https://skillrock.onrender.com/static/img/skillrock-og-banner.png"', content)
        self.assertIn('property="og:image:width" content="1200"', content)
        self.assertIn('property="og:image:height" content="630"', content)

        # JSON-LD Schema
        self.assertIn('"@type": "EducationalOrganization"', content)
        self.assertIn('"@type": "WebSite"', content)
        self.assertIn('"@type": "SearchAction"', content)

    def test_course_detail_seo_and_breadcrumbs(self):
        """Verify course detail page has course schema, breadcrumbs schema, and canonical URL."""
        from models import Course
        with self.app.app_context():
            courses = Course.get_published_courses()
            slug = courses[0].slug if courses else "java-core-oops-masterclass"

        res = self.client.get(f"/learning/courses/{slug}")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")

        # Canonical tag
        self.assertIn(f'<link rel="canonical" href="https://skillrock.onrender.com/learning/courses/{slug}">', content)

        # Single H1 tag
        self.assertEqual(content.count("<h1"), 1)

        # BreadcrumbList schema
        self.assertIn('"@type": "BreadcrumbList"', content)
        self.assertIn('"name": "Courses"', content)
        self.assertIn('"@type": "Course"', content)

    def test_auth_pages_noindex(self):
        """Verify private/auth pages render noindex, nofollow to prevent indexation."""
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn('content="noindex, nofollow"', content)

    def test_404_error_code_and_noindex(self):
        """Verify nonexistent routes return true HTTP 404 and have noindex, nofollow."""
        res = self.client.get("/completely-nonexistent-path-for-seo-test-404")
        self.assertEqual(res.status_code, 404)
        content = res.data.decode("utf-8")
        self.assertIn('content="noindex, nofollow"', content)
        self.assertIn("Page Not Found", content)

if __name__ == "__main__":
    unittest.main()
