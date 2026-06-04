from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


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
