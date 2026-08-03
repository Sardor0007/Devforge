from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Service, Order, Review
from decimal import Decimal

User = get_user_model()

class MarketplaceViewsTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.seller = User.objects.create_user(
            username='seller', email='seller@test.com', password='passuser123'
        )
        self.seller.subscription_type = 'gold'
        self.seller.save()

        self.buyer = User.objects.create_user(
            username='buyer', email='buyer@test.com', password='passuser123'
        )
        self.buyer.balance = Decimal('100.00')
        self.buyer.save()

        self.service = Service.objects.create(
            seller=self.seller,
            title="3D Asset modeling",
            description="High quality asset modeling",
            category="3d_modeling",
            price=Decimal('20.00'),
            delivery_days=3
        )

    def test_service_list_view(self):
        resp = self.c.get(reverse('service_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "3D Asset modeling")

    def test_service_detail_view(self):
        resp = self.c.get(reverse('service_detail', kwargs={'pk': self.service.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "3D Asset modeling")

    def test_service_create_view(self):
        self.c.login(username='seller@test.com', password='passuser123')
        resp = self.c.post(reverse('service_create'), {
            'title': 'Another Service',
            'description': 'Unique design for game HUD',
            'category': 'ui_design',
            'price': '30.00',
            'delivery_days': '5'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Service.objects.filter(title='Another Service').exists())

    def test_order_create_view(self):
        self.c.login(username='buyer@test.com', password='passuser123')
        # Service price is $20.00, buyer has $100.00.
        resp = self.c.post(reverse('order_create', kwargs={'pk': self.service.pk}), {
            'requirements': 'Make it low poly'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Order.objects.filter(buyer=self.buyer, service=self.service).exists())
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.balance, Decimal('80.00'))

    def test_order_list_view(self):
        self.c.login(username='buyer@test.com', password='passuser123')
        resp = self.c.get(reverse('order_list'))
        self.assertEqual(resp.status_code, 200)

    def test_order_confirm_view(self):
        order = Order.objects.create(
            buyer=self.buyer,
            service=self.service,
            amount=Decimal('20.00'),
            deadline='2026-06-10'
        )
        self.c.login(username='seller@test.com', password='passuser123')
        resp = self.c.post(reverse('order_confirm', kwargs={'pk': order.pk}))
        self.assertEqual(resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'active')
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance, Decimal('20.00'))
