"""
Jobs app — keng qamrovli testlar
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from .models import Job, Proposal, EscrowPayment, Delivery, Dispute

User = get_user_model()


class JobModelTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='client', email='client@test.com', password='pass123'
        )
        self.worker_user = User.objects.create_user(
            username='worker', email='worker@test.com', password='pass123',
            subscription_type='gold'
        )
        self.job = Job.objects.create(
            client=self.client_user,
            title='Unity Dasturchi Kerak',
            description='FPS o\'yin uchun controller scripting',
            budget=Decimal('500.00'),
            status='open'
        )

    def test_job_creation(self):
        self.assertEqual(self.job.title, 'Unity Dasturchi Kerak')
        self.assertEqual(self.job.client, self.client_user)
        self.assertEqual(self.job.status, 'open')
        self.assertEqual(self.job.budget, Decimal('500.00'))

    def test_job_default_visibility(self):
        self.assertEqual(self.job.visibility, 'public')

    def test_job_ordering(self):
        job2 = Job.objects.create(
            client=self.client_user, title='Second Job',
            description='...', budget=100
        )
        jobs = list(Job.objects.all())
        self.assertEqual(jobs[0], job2)  # Eng yangi birinchi

    def test_check_auto_approval_no_delivery(self):
        self.job.status = 'submitted'
        self.job.save()
        result = self.job.check_auto_approval()
        self.assertFalse(result)  # Delivery yo'q


class ProposalModelTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='c2', email='c2@test.com', password='pass123'
        )
        self.worker = User.objects.create_user(
            username='w2', email='w2@test.com', password='pass123'
        )
        self.job = Job.objects.create(
            client=self.client_user, title='Job', description='Desc', budget=100
        )

    def test_proposal_creation(self):
        proposal = Proposal.objects.create(
            job=self.job,
            worker=self.worker,
            price=Decimal('80.00'),
            message='Men bu ishni qila olaman',
            delivery_days=7
        )
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(proposal.price, Decimal('80.00'))

    def test_proposal_unique_together(self):
        Proposal.objects.create(
            job=self.job, worker=self.worker,
            price=80, message='First', delivery_days=7
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Proposal.objects.create(
                job=self.job, worker=self.worker,
                price=90, message='Second', delivery_days=5
            )


class EscrowPaymentTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='ec', email='ec@test.com', password='pass',
            balance=Decimal('1000.00')
        )
        self.worker = User.objects.create_user(
            username='ew', email='ew@test.com', password='pass'
        )
        self.job = Job.objects.create(
            client=self.client_user, title='Escrow Job',
            description='Test', budget=Decimal('200.00'),
            selected_worker=self.worker
        )

    def test_escrow_creation(self):
        fee = Decimal('12.00')  # 6% of 200
        escrow = EscrowPayment.objects.create(
            job=self.job,
            client=self.client_user,
            worker=self.worker,
            amount=Decimal('200.00'),
            platform_fee=fee
        )
        self.assertEqual(escrow.status, 'pending')
        self.assertEqual(escrow.amount, Decimal('200.00'))
        self.assertEqual(escrow.platform_fee, fee)

    def test_escrow_str(self):
        escrow = EscrowPayment.objects.create(
            job=self.job, client=self.client_user,
            worker=self.worker, amount=200, platform_fee=12
        )
        self.assertIn('Escrow', str(escrow))


class JobViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_user = User.objects.create_user(
            username='vc', email='vc@test.com', password='pass123'
        )
        self.job = Job.objects.create(
            client=self.client_user,
            title='Public Job',
            description='Test job',
            budget=100,
            visibility='public'
        )

    def test_job_list_view_anonymous(self):
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Job')

    def test_job_detail_view(self):
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)

    def test_job_create_requires_login(self):
        response = self.client.get(reverse('job_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_job_create_authenticated(self):
        self.client.login(username='vc@test.com', password='pass123')
        response = self.client.get(reverse('job_create'))
        self.assertEqual(response.status_code, 200)

    def test_my_jobs_requires_login(self):
        response = self.client.get(reverse('my_jobs'))
        self.assertEqual(response.status_code, 302)
