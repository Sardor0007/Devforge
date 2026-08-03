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
