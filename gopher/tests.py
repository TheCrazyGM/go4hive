from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class GopherViewTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Go4Hive")

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
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Go4Hive")
