"""
Projects app — keng qamrovli testlar
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Project, ProjectRole, ProjectMember, Task

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='creator', email='creator@test.com', password='pass123'
        )
        self.project = Project.objects.create(
            title='Epic RPG',
            description='Open world RPG o\'yini',
            creator=self.user,
            genre='rpg',
            status='planning'
        )

    def test_project_creation(self):
        self.assertEqual(self.project.title, 'Epic RPG')
        self.assertEqual(self.project.creator, self.user)
        self.assertEqual(self.project.genre, 'rpg')
        self.assertEqual(self.project.status, 'planning')

    def test_project_str(self):
        self.assertEqual(str(self.project), 'Epic RPG')

    def test_project_default_visibility(self):
        self.assertEqual(self.project.visibility, 'public')

    def test_project_default_max_members(self):
        self.assertEqual(self.project.max_members, 10)

    def test_member_count_empty(self):
        self.assertEqual(self.project.member_count, 0)

    def test_member_count_with_members(self):
        member = User.objects.create_user(
            username='member1', email='m1@test.com', password='pass'
        )
        role = ProjectRole.objects.create(
            project=self.project, role_type='developer'
        )
        ProjectMember.objects.create(
            project=self.project, user=member,
            role=role, is_approved=True
        )
        self.assertEqual(self.project.member_count, 1)

    def test_ordering(self):
        p2 = Project.objects.create(
            title='Second Project', description='...', creator=self.user
        )
        projects = list(Project.objects.all())
        self.assertEqual(projects[0], p2)  # Eng yangi birinchi


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='taskuser', email='task@test.com', password='pass'
        )
        self.project = Project.objects.create(
            title='Task Project', description='...', creator=self.user
        )

    def test_task_creation(self):
        task = Task.objects.create(
            project=self.project,
            title='Asosiy menyu yaratish',
            description='Unity UI orqali',
            status='todo',
            priority='high'
        )
        self.assertEqual(task.title, 'Asosiy menyu yaratish')
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.priority, 'high')

    def test_task_str(self):
        task = Task.objects.create(
            project=self.project, title='Test Task', description=''
        )
        self.assertIn('Task Project', str(task))
        self.assertIn('Test Task', str(task))

    def test_task_assigned_to_null(self):
        task = Task.objects.create(
            project=self.project, title='Unassigned', description=''
        )
        self.assertIsNone(task.assigned_to)


class ProjectRoleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ru', email='ru@test.com', password='pass'
        )
        self.project = Project.objects.create(
            title='Role Project', description='...', creator=self.user
        )

    def test_role_creation(self):
        role = ProjectRole.objects.create(
            project=self.project,
            role_type='artist',
            description='3D model yaratadi',
            required_skills='Blender, ZBrush'
        )
        self.assertEqual(role.role_type, 'artist')
        self.assertFalse(role.is_filled)

    def test_open_roles_count(self):
        ProjectRole.objects.create(project=self.project, role_type='developer')
        ProjectRole.objects.create(project=self.project, role_type='artist')
        ProjectRole.objects.create(project=self.project, role_type='designer', is_filled=True)
        self.assertEqual(self.project.open_roles_count, 2)


from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ProjectDownloadPermission


class ProjectDownloadTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            username='owner', email='owner@test.com', password='pass', subscription_type='free'
        )
        self.pro_user = User.objects.create_user(
            username='prouser', email='pro@test.com', password='pass', subscription_type='pro'
        )
        self.free_user = User.objects.create_user(
            username='freeuser', email='free@test.com', password='pass', subscription_type='free'
        )
        dummy_file = SimpleUploadedFile("project.zip", b"fake zip content", content_type="application/zip")
        self.project = Project.objects.create(
            title='Downloadable Game',
            description='Test game',
            creator=self.creator,
            project_file=dummy_file,
            download_enabled=True
        )

    def test_owner_can_download(self):
        self.client.force_login(self.creator)
        url = reverse('project_download', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment;', response['Content-Disposition'])

    def test_free_user_cannot_download(self):
        self.client.force_login(self.free_user)
        # Hatto ruxsat berilgan taqdirda ham free foydalanuvchi yuklab ololmaydi
        ProjectDownloadPermission.objects.create(project=self.project, user=self.free_user, granted_by=self.creator)
        url = reverse('project_download', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_pro_user_without_permission_cannot_download(self):
        self.client.force_login(self.pro_user)
        url = reverse('project_download', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_pro_user_with_permission_can_download(self):
        ProjectDownloadPermission.objects.create(project=self.project, user=self.pro_user, granted_by=self.creator)
        self.client.force_login(self.pro_user)
        url = reverse('project_download', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"fake zip content")

    def test_grant_and_revoke_download(self):
        self.client.force_login(self.creator)
        grant_url = reverse('project_grant_download', kwargs={'pk': self.project.pk, 'user_pk': self.pro_user.pk})
        self.client.post(grant_url)
        self.assertTrue(ProjectDownloadPermission.objects.filter(project=self.project, user=self.pro_user).exists())

        revoke_url = reverse('project_revoke_download', kwargs={'pk': self.project.pk, 'user_pk': self.pro_user.pk})
        self.client.post(revoke_url)
        self.assertFalse(ProjectDownloadPermission.objects.filter(project=self.project, user=self.pro_user).exists())

    def test_toggle_download(self):
        self.client.force_login(self.creator)
        toggle_url = reverse('project_toggle_download', kwargs={'pk': self.project.pk})
        self.client.post(toggle_url)
        self.project.refresh_from_db()
        self.assertFalse(self.project.download_enabled)
        self.client.post(toggle_url)
        self.project.refresh_from_db()
        self.assertTrue(self.project.download_enabled)
