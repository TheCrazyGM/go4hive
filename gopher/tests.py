from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.http import HttpResponse
from core.middleware import BrowserCheckMiddleware


class GopherViewTests(TestCase):
    def test_index_loads(self):
        import tomllib
        from django.conf import settings

        with open(settings.BASE_DIR / "pyproject.toml", "rb") as f:
            version = tomllib.load(f)["project"]["version"]

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Go4Hive")
        self.assertContains(response, f"Go4Hive v{version}")

    @patch("gopher.views.get_trending_posts")
    def test_trending_loads(self, mock_get_trending):
        mock_get_trending.return_value = [
            {
                "title": "Test Post",
                "authorperm": "test/perm",
                "author": "test",
                "net_votes": 1,
                "children": 0,
                "payout": 0.0,
            }
        ]
        response = self.client.get(reverse("trending"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")

    def test_about_loads(self):
        import tomllib
        from django.conf import settings

        with open(settings.BASE_DIR / "pyproject.toml", "rb") as f:
            version = tomllib.load(f)["project"]["version"]

        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Go4Hive")
        self.assertContains(response, f"VERSION: {version}")
        self.assertContains(response, "ANTIGRAVITY CLI")

    def test_clear_cache_anonymous(self):
        response = self.client.get(reverse("admin_clear_cache"))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse("admin_clear_cache"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_clear_cache_staff(self):
        from django.contrib.auth.models import User
        from django.core.cache import cache

        staff_user = User.objects.create_user(
            username="staff", password="pwd", is_staff=True
        )
        self.client.force_login(staff_user)

        cache.set("test_key", "test_val")
        self.assertEqual(cache.get("test_key"), "test_val")

        response = self.client.post(reverse("admin_clear_cache"))
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(cache.get("test_key"))

    def test_admin_index_loads_for_staff(self):
        from django.contrib.auth.models import User

        staff_user = User.objects.create_user(
            username="staff2", password="pwd", is_staff=True
        )
        self.client.force_login(staff_user)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dump Cache")


class BrowserCheckMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda req: HttpResponse("SUCCESS")
        self.middleware = BrowserCheckMiddleware(self.get_response)

    def test_bypass_whitelist(self):
        # Whitelisted paths should bypass the check and return SUCCESS
        for path in ["/static/gopher/css/terminal.css", "/robots.txt", "/favicon.ico"]:
            request = self.factory.get(path)
            with patch("sys.argv", ["manage.py"]):
                response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"SUCCESS")

    def test_missing_cookie_serves_challenge(self):
        # A normal path without cookie should serve the challenge page
        request = self.factory.get("/")
        with patch("sys.argv", ["manage.py"]):
            response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Go4Hive Security Check")
        self.assertContains(response, "TESTING JAVASCRIPT CAPABILITIES")
        self.assertNotEqual(response.content, b"SUCCESS")

    def test_existing_cookie_bypasses_challenge(self):
        # A request with d_sensor cookie should bypass the challenge and return SUCCESS
        request = self.factory.get("/")
        request.COOKIES["d_sensor"] = "1234567890"
        with patch("sys.argv", ["manage.py"]):
            response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"SUCCESS")

    def test_theme_color_applied(self):
        # Test that proper theme variables are rendered in the HTML for each theme
        themes = {
            "green": ("#00ff41", "#008f11", "#003b00"),
            "amber": ("#ffb000", "#a37200", "#3b2a00"),
            "white": ("#e0e0e0", "#888888", "#333333"),
        }
        for theme_name, (text, dim, highlight) in themes.items():
            request = self.factory.get("/")

            class DummySession(dict):
                pass

            request.session = DummySession({"theme": theme_name})
            with patch("sys.argv", ["manage.py"]):
                response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
            html = response.content.decode("utf-8")
            self.assertIn(f"--text-color: {text}", html)
            self.assertIn(f"--dim-color: {dim}", html)
            self.assertIn(f"--highlight-color: {highlight}", html)
