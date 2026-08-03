from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

User = get_user_model()

class AnalyticsViewsTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.admin = User.objects.create_superuser(
            username='adminuser', email='admin@test.com', password='adminpass123'
        )
        self.user = User.objects.create_user(
            username='regularuser', email='user@test.com', password='userpass123'
        )

    def test_analytics_dashboard_requires_staff(self):
        # Anonymous user gets redirected
        resp = self.c.get(reverse('analytics_dashboard'))
        self.assertEqual(resp.status_code, 302)

        # Regular user gets redirected or blocked
        self.c.login(username='user@test.com', password='userpass123')
        resp = self.c.get(reverse('analytics_dashboard'))
        self.assertEqual(resp.status_code, 302)

        # Admin user succeeds
        self.c.login(username='admin@test.com', password='adminpass123')
        resp = self.c.get(reverse('analytics_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_toggle_user_active(self):
        self.c.login(username='admin@test.com', password='adminpass123')
        # Check initial active status
        self.assertTrue(self.user.is_active)

        # Toggle active status
        resp = self.c.post(reverse('user_toggle_active', kwargs={'pk': self.user.pk}))
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_toggle_user_verified(self):
        self.c.login(username='admin@test.com', password='adminpass123')
        resp = self.c.post(reverse('user_toggle_verified', kwargs={'pk': self.user.pk}))
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_update_user_balance(self):
        self.c.login(username='admin@test.com', password='adminpass123')
        resp = self.c.post(reverse('admin_update_balance', kwargs={'pk': self.user.pk}), {
            'balance': '150.50'
        })
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal('150.50'))
