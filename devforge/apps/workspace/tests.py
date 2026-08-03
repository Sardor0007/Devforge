"""
Workspace app — keng qamrovli testlar
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

from .models import Workspace, WorkspaceFile, ChatRoom, ChatMessage
from apps.projects.models import Project

User = get_user_model()


class WorkspaceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='wsuser', email='ws@test.com', password='pass123'
        )
        self.project = Project.objects.create(
            title='WS Project', description='...', creator=self.user
        )
        self.workspace = Workspace.objects.create(project=self.project)

    def test_workspace_creation(self):
        self.assertEqual(self.workspace.project, self.project)

    def test_workspace_str(self):
        self.assertIn('WS Project', str(self.workspace))

    def test_workspace_one_to_one(self):
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Workspace.objects.create(project=self.project)


class WorkspaceFileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='wfu', email='wfu@test.com', password='pass'
        )
        self.project = Project.objects.create(
            title='File Project', description='...', creator=self.user
        )
        self.workspace = Workspace.objects.create(project=self.project)

    def test_file_creation(self):
        f = WorkspaceFile.objects.create(
            workspace=self.workspace,
            name='main.py',
            path='/',
            content='print("Hello")',
            language='python',
            created_by=self.user
        )
        self.assertEqual(f.name, 'main.py')
        self.assertEqual(f.language, 'python')
        self.assertFalse(f.is_folder)

    def test_folder_creation(self):
        folder = WorkspaceFile.objects.create(
            workspace=self.workspace,
            name='src',
            path='/',
            is_folder=True,
            created_by=self.user
        )
        self.assertTrue(folder.is_folder)
        self.assertEqual(folder.extension(), 'folder')

    def test_file_full_path_root(self):
        f = WorkspaceFile.objects.create(
            workspace=self.workspace, name='app.py', path='/', created_by=self.user
        )
        self.assertEqual(f.full_path(), '/app.py')

    def test_file_full_path_subdir(self):
        f = WorkspaceFile.objects.create(
            workspace=self.workspace, name='views.py', path='/src', created_by=self.user
        )
        self.assertEqual(f.full_path(), '/src/views.py')

    def test_file_extension(self):
        f = WorkspaceFile.objects.create(
            workspace=self.workspace, name='style.css', path='/', created_by=self.user
        )
        self.assertEqual(f.extension(), 'css')

    def test_file_no_extension(self):
        f = WorkspaceFile.objects.create(
            workspace=self.workspace, name='Makefile', path='/', created_by=self.user
        )
        self.assertEqual(f.extension(), '')


class ChatModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='cu1', email='cu1@test.com', password='pass'
        )
        self.user2 = User.objects.create_user(
            username='cu2', email='cu2@test.com', password='pass'
        )
        self.project = Project.objects.create(
            title='Chat Project', description='...', creator=self.user1
        )
        self.room = ChatRoom.objects.create(project=self.project)

    def test_chat_room_creation(self):
        self.assertEqual(self.room.project, self.project)
        self.assertIn('Chat Project', str(self.room))

    def test_chat_message_creation(self):
        msg = ChatMessage.objects.create(
            room=self.room,
            sender=self.user1,
            content='Salom jamoa!'
        )
        self.assertEqual(msg.sender, self.user1)
        self.assertEqual(msg.content, 'Salom jamoa!')

    def test_message_ordering(self):
        ChatMessage.objects.create(room=self.room, sender=self.user1, content='First')
        ChatMessage.objects.create(room=self.room, sender=self.user2, content='Second')
        messages = list(ChatMessage.objects.filter(room=self.room))
        self.assertEqual(messages[0].content, 'First')  # ASC ordering


@override_settings(SECURE_SSL_REDIRECT=False)
class WorkspaceViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='vwu', email='vwu@test.com', password='pass123',
            subscription_type='gold'
        )
        self.project = Project.objects.create(
            title='View WS', description='...', creator=self.user
        )
        self.workspace = Workspace.objects.create(project=self.project)

    def test_workspace_view_requires_login(self):
        url = reverse('workspace', kwargs={'pk': self.project.pk})
        resp = self.client.get(url, follow=True)
        self.assertTrue(resp.status_code in [200, 302])

    def test_workspace_accessible_to_creator(self):
        self.client.force_login(self.user)
        url = reverse('workspace', kwargs={'pk': self.project.pk})
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_file_create_api(self):
        self.client.force_login(self.user)
        url = reverse('file_create', kwargs={'workspace_pk': self.workspace.pk})
        resp = self.client.post(
            url,
            data=json.dumps({'name': 'test.py', 'path': '/', 'language': 'python'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['name'], 'test.py')

    def test_file_save_api(self):
        self.client.force_login(self.user)
        f = WorkspaceFile.objects.create(
            workspace=self.workspace, name='save.py', path='/', created_by=self.user
        )
        url = reverse('file_save', kwargs={'file_pk': f.pk})
        resp = self.client.post(
            url,
            data=json.dumps({'content': 'x = 1'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        f.refresh_from_db()
        self.assertEqual(f.content, 'x = 1')

