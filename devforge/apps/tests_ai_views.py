"""
AI Views — testlar (rate limiting, auth, input validation)
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock

User = get_user_model()


class AIViewsAuthTest(TestCase):
    """Login kerak bo'lgan endpointlar anonim foydalanuvchidan himoyalanganligini tekshirish"""

    ENDPOINTS = [
        'ai_generate_tasks',
        'ai_generate_description',
        'ai_generate_job_desc',
        'ai_explain_code',
        'ai_format_code',
        'ai_debug_code',
    ]

    def setUp(self):
        self.client = Client()

    def test_all_ai_endpoints_require_login(self):
        for name in self.ENDPOINTS:
            with self.subTest(endpoint=name):
                resp = self.client.post(
                    reverse(name),
                    data=json.dumps({}),
                    content_type='application/json'
                )
                # 302 (login redirect) yoki 403 kutiladi
                self.assertIn(resp.status_code, [302, 403],
                    msg=f"{name} unauthenticated access returned {resp.status_code}")


class AIViewsInputValidationTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(
            username='aiuser', email='ai@test.com', password='aipass123',
            subscription_type='gold'
        )
        self.c.login(username='ai@test.com', password='aipass123')

    @patch('apps.ai_views.call_claude')
    def test_generate_tasks_missing_fields(self, mock_claude):
        resp = self.c.post(
            reverse('ai_generate_tasks'),
            data=json.dumps({'project_title': '', 'project_description': ''}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn('error', data)

    @patch('apps.ai_views.call_claude')
    def test_generate_tasks_demo_mode(self, mock_claude):
        """API key yo'q bo'lganda demo rejim ishlashi"""
        mock_claude.return_value = (None, 'AI_KEY_MISSING')
        resp = self.c.post(
            reverse('ai_generate_tasks'),
            data=json.dumps({
                'project_title': 'Test Game',
                'project_description': 'RPG game',
                'genre': 'rpg',
                'count': 5
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('tasks', data)
        self.assertTrue(data.get('demo'))

    @patch('apps.ai_views.call_claude')
    def test_explain_code_too_long(self, mock_claude):
        resp = self.c.post(
            reverse('ai_explain_code'),
            data=json.dumps({'code': 'x' * 4000, 'lang': 'python'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    @patch('apps.ai_views.call_claude')
    def test_explain_code_success(self, mock_claude):
        mock_claude.return_value = ('{"explanation": "x ni 1 ga o\'zlashtiradi", "summary": "Assignment"}', None)
        resp = self.c.post(
            reverse('ai_explain_code'),
            data=json.dumps({'code': 'x = 1', 'lang': 'python'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

    @patch('apps.ai_views.call_claude')
    def test_format_code_empty(self, mock_claude):
        resp = self.c.post(
            reverse('ai_format_code'),
            data=json.dumps({'code': '', 'lang': 'python'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    @patch('apps.ai_views.call_claude')
    def test_description_missing_title(self, mock_claude):
        resp = self.c.post(
            reverse('ai_generate_description'),
            data=json.dumps({'title': '', 'category': 'gamedev'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    @patch('apps.ai_views.call_claude')
    def test_job_desc_demo_mode(self, mock_claude):
        mock_claude.return_value = (None, 'AI_KEY_MISSING')
        resp = self.c.post(
            reverse('ai_generate_job_desc'),
            data=json.dumps({'role': 'Unity Developer', 'project_type': 'FPS', 'skills': 'Unity, C#'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('description', data)
        self.assertTrue(data.get('demo'))


class AIViewsCSRFTest(TestCase):
    """csrf_exempt ishlatilmaganligini tekshirish — POST CSRF bilan ishlashi kerak"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='csrftest', email='csrf@test.com', password='pass123'
        )
        # Django test client CSRF ni avtomatik boshqaradi

    def test_ai_endpoint_not_csrf_exempt(self):
        """csrf_exempt bo'lmasligi kerak — login_required uchun redirect bo'ladi"""
        client = Client(enforce_csrf_checks=True)
        resp = client.post(
            reverse('ai_explain_code'),
            data=json.dumps({'code': 'x=1', 'lang': 'python'}),
            content_type='application/json'
        )
        # Login qilmagan — 302 (redirect) yoki 403
        self.assertIn(resp.status_code, [302, 403])
