from django.test import TestCase
from django.conf import settings

class SupabaseDBTestCase(TestCase):
    def test_db_url(self):
        DATABASE_URL = settings.DATABASE_URL
        self.assertIn('neon.tech', DATABASE_URL)
