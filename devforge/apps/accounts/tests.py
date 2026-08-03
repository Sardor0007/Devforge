"""
Accounts app — keng qamrovli testlar
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@devforge.uz',
            password='securepass123',
            role='developer'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@devforge.uz')
        self.assertEqual(self.user.role, 'developer')
        self.assertEqual(self.user.subscription_type, 'free')
        self.assertEqual(self.user.balance, Decimal('0.00'))
        self.assertEqual(self.user.xp, 0)
        self.assertEqual(self.user.level, 1)

    def test_user_str(self):
        self.assertIn('testuser', str(self.user))
        self.assertIn('test@devforge.uz', str(self.user))

    def test_full_name_property(self):
        self.user.first_name = 'Ali'
        self.user.last_name = 'Valiyev'
        self.assertEqual(self.user.full_name, 'Ali Valiyev')

    def test_full_name_fallback(self):
        # First/last not set — username qaytariladi
        self.assertEqual(self.user.full_name, 'testuser')

    def test_can_use_pro_features_free(self):
        self.assertFalse(self.user.can_use_pro_features())

    def test_can_use_pro_features_gold(self):
        self.user.subscription_type = 'gold'
        self.assertTrue(self.user.can_use_pro_features())

    def test_can_use_pro_features_platinum(self):
        self.user.subscription_type = 'platinum'
        self.assertTrue(self.user.can_use_pro_features())

    def test_upload_limit_free(self):
        self.assertEqual(self.user.get_upload_limit(), 0)

    def test_upload_limit_gold(self):
        self.user.subscription_type = 'gold'
        self.assertEqual(self.user.get_upload_limit(), 10)

    def test_upload_limit_platinum(self):
        self.user.subscription_type = 'platinum'
        self.assertEqual(self.user.get_upload_limit(), 50)

    def test_add_xp_no_levelup(self):
        self.user.add_xp(50)
        self.assertEqual(self.user.xp, 50)
        self.assertEqual(self.user.level, 1)

    def test_add_xp_levelup(self):
        # Level 1 → XP target: (1 * 100) * 1.5 = 150
        self.user.add_xp(200)
        self.assertGreater(self.user.level, 1)

    def test_level_progress(self):
        self.user.xp = 75
        progress = self.user.level_progress
        self.assertGreaterEqual(progress, 0)
        self.assertLessEqual(progress, 100)


class UserBalanceTest(TestCase):
    def setUp(self):
        from apps.accounts.models import UserBalance
        self.user = User.objects.create_user(
            username='richuser', email='rich@devforge.uz', password='pass123'
        )
        self.wallet, _ = UserBalance.objects.get_or_create(user=self.user)

    def test_deposit_credit(self):
        self.wallet.credit(Decimal('500.00'), description='Test deposit')
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.deposit_balance, Decimal('500.00'))

    def test_deposit_debit(self):
        self.wallet.credit(Decimal('500.00'), description='Test deposit')
        self.wallet.debit(Decimal('100.00'), description='Test purchase')
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.deposit_balance, Decimal('400.00'))

    def test_earnings_earn_and_withdraw(self):
        self.wallet.earn(Decimal('200.00'), description='Test sale')
        self.wallet.withdraw(Decimal('50.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.earnings_balance, Decimal('150.00'))

    def test_transfer_earnings_to_deposit(self):
        self.wallet.earn(Decimal('100.00'), description='Test earn')
        self.wallet.transfer_to_deposit(Decimal('40.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.earnings_balance, Decimal('60.00'))
        self.assertEqual(self.wallet.deposit_balance, Decimal('40.00'))

    def test_cannot_transfer_deposit_to_earnings(self):
        """Depazitdan foydaga o'tkazib bo'lmaydi - faqat withdraw/transfer_to_deposit"""
        self.wallet.credit(Decimal('100.00'))
        # Modelda bunday metod yo'q - bu test mavjud metodlarning cheklovini tasdiqlaydi
        self.assertFalse(hasattr(self.wallet, 'transfer_to_earnings'))


class TransactionModelTest(TestCase):
    def setUp(self):
        from apps.accounts.models import Transaction
        self.Transaction = Transaction
        self.user = User.objects.create_user(
            username='txuser', email='tx@devforge.uz', password='pass123'
        )

    def test_transaction_creation(self):
        tx = self.Transaction.objects.create(
            user=self.user,
            amount=Decimal('25.00'),
            transaction_type='deposit',
            description='Test deposit'
        )
        self.assertEqual(tx.user, self.user)
        self.assertEqual(tx.amount, Decimal('25.00'))
        self.assertEqual(tx.transaction_type, 'deposit')

    def test_transaction_ordering(self):
        self.Transaction.objects.create(user=self.user, amount=10, transaction_type='deposit', description='First')
        self.Transaction.objects.create(user=self.user, amount=20, transaction_type='deposit', description='Second')
        txs = list(self.Transaction.objects.filter(user=self.user))
        # En yangi birinchi (ordering = ['-created_at'])
        self.assertEqual(txs[0].description, 'Second')
