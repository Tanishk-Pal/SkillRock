import unittest
import xml.etree.ElementTree as ET
import json
from app import create_app
from models import Course, User, Certificate

class TestMobileSeoPwa(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_pwa_manifest_endpoint(self):
        """Verify /manifest.json returns valid JSON with correct PWA properties."""
        res = self.client.get("/manifest.json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/manifest+json", res.content_type)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data.get("name"), "SkillRock — Learn, Build & Certify")
        self.assertEqual(data.get("short_name"), "SkillRock")
        self.assertEqual(data.get("display"), "standalone")
        self.assertEqual(data.get("start_url"), "/")
        icons = data.get("icons", [])
        self.assertTrue(len(icons) >= 2)
        icon_srcs = [i["src"] for i in icons]
        self.assertIn("/static/img/icon-192.png", icon_srcs)
        self.assertIn("/static/img/icon-512.png", icon_srcs)

    def test_pwa_service_worker_endpoint(self):
        """Verify /sw.js is served at root scope with Service-Worker-Allowed header."""
        res = self.client.get("/sw.js")
        self.assertEqual(res.status_code, 200)
        self.assertIn("javascript", res.content_type)
        self.assertEqual(res.headers.get("Service-Worker-Allowed"), "/")
        self.assertTrue("skillrock-v1." in res.data.decode("utf-8"))

    def test_sitemap_xml_contains_courses(self):
        """Verify /sitemap.xml generates well-formed XML including dynamic courses."""
        res = self.client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/xml", res.content_type)
        xml_data = res.data.decode("utf-8")
        
        # Parse XML tree
        root = ET.fromstring(xml_data)
        self.assertTrue(root.tag.endswith("urlset"))
        
        # Verify courses and main URLs are present
        urls = [elem.text for elem in root.iter() if elem.tag.endswith("loc")]
        self.assertTrue(any("/courses" in u for u in urls))
        
        courses = Course.get_published_courses() or []
        if courses:
            first_course = courses[0]
            if first_course.slug:
                self.assertTrue(any(first_course.slug in u for u in urls), f"Course {first_course.slug} missing from sitemap")

    def test_robots_txt_format(self):
        """Verify /robots.txt directives and sitemap reference."""
        res = self.client.get("/robots.txt")
        self.assertEqual(res.status_code, 200)
        text = res.data.decode("utf-8")
        self.assertIn("User-agent: *", text)
        self.assertIn("Allow: /", text)
        self.assertIn("Sitemap:", text)
        self.assertIn("/sitemap.xml", text)

    def test_course_detail_schema_and_mobile_card(self):
        """Verify course detail page has Schema.org Course JSON-LD and mobile action card."""
        courses = Course.get_published_courses() or []
        if courses:
            c = courses[0]
            res = self.client.get(f"/learning/courses/{c.slug}")
            self.assertEqual(res.status_code, 200)
            html = res.data.decode("utf-8")
            self.assertIn('"@type": "Course"', html)
            self.assertIn('mobile-course-action-card', html)
            self.assertIn('course-about-container', html)

if __name__ == "__main__":
    unittest.main()
