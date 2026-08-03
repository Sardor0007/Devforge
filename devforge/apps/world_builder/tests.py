"""
World Builder App — unit and integration tests (Dashboard, Editor, Create, Save, Rename, Delete)
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
from decimal import Decimal

from apps.world_builder.models import WorldMap

User = get_user_model()


class WorldBuilderTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(
            username='builder', email='builder@devforge.uz', password='pass123',
            subscription_type='gold'
        )
        self.other_user = User.objects.create_user(
            username='stranger', email='stranger@devforge.uz', password='pass123',
            subscription_type='gold'
        )
        
        # Create a starting map
        self.map = WorldMap.objects.create(
            title='My Dungeon',
            owner=self.user,
            map_type='dungeon',
            data={'version': 2, 'objects': [], 'layers': [], 'groups': []}
        )

    def test_dashboard_requires_login(self):
        resp = self.c.get(reverse('world_builder:dashboard'))
        self.assertEqual(resp.status_code, 302)

    def test_dashboard_accessible_when_logged_in(self):
        self.c.login(username='builder@devforge.uz', password='pass123')
        resp = self.c.get(reverse('world_builder:dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'My Dungeon')

    def test_create_map_requires_login(self):
        resp = self.c.post(reverse('world_builder:create_map'), {'title': 'New Map', 'map_type': 'castle'})
        self.assertEqual(resp.status_code, 302)

    def test_create_map_success(self):
        self.c.login(username='builder@devforge.uz', password='pass123')
        resp = self.c.post(reverse('world_builder:create_map'), {
            'title': 'Awesome Castle',
            'map_type': 'castle'
        })
        # Should redirect to the editor view of the new map
        self.assertEqual(resp.status_code, 302)
        new_map = WorldMap.objects.filter(title='Awesome Castle').first()
        self.assertIsNotNone(new_map)
        self.assertEqual(new_map.owner, self.user)
        self.assertEqual(new_map.map_type, 'castle')
        self.assertEqual(new_map.data['version'], 2)

    def test_editor_view_requires_login(self):
        resp = self.c.get(reverse('world_builder:editor', kwargs={'map_id': self.map.id}))
        self.assertEqual(resp.status_code, 302)

    def test_editor_view_owner_only(self):
        # Logged in as other user, should get 404
        self.c.login(username='stranger@devforge.uz', password='pass123')
        resp = self.c.get(reverse('world_builder:editor', kwargs={'map_id': self.map.id}))
        self.assertEqual(resp.status_code, 404)

    def test_editor_view_owner_success(self):
        self.c.login(username='builder@devforge.uz', password='pass123')
        resp = self.c.get(reverse('world_builder:editor', kwargs={'map_id': self.map.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'My Dungeon')

    def test_save_map_success(self):
        self.c.login(username='builder@devforge.uz', password='pass123')
        payload = {
            'data': {
                'version': 2,
                'gridSize': 30,
                'objects': [{'id': 'o1', 'type': 'rect', 'x': 10, 'y': 20}],
                'layers': [],
                'groups': []
            },
            'title': 'My Epic Dungeon'
        }
        resp = self.c.post(
            reverse('world_builder:save_map', kwargs={'map_id': self.map.id}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'success')
        
        self.map.refresh_from_db()
        self.assertEqual(self.map.title, 'My Epic Dungeon')
        self.assertEqual(self.map.data['gridSize'], 30)

    def test_save_map_invalid_payload(self):
        self.c.login(username='builder@devforge.uz', password='pass123')
        resp = self.c.post(
            reverse('world_builder:save_map', kwargs={'map_id': self.map.id}),
            data=json.dumps({'data': 'not-a-dict'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_rename_map_success(self):
        self.c.login(username='builder@devforge.uz', password='pass123')
        resp = self.c.post(
            reverse('world_builder:rename_map', kwargs={'map_id': self.map.id}),
            data=json.dumps({'title': 'Renamed Dungeon'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.map.refresh_from_db()
        self.assertEqual(self.map.title, 'Renamed Dungeon')

    def test_delete_map_requires_login(self):
        resp = self.c.get(reverse('world_builder:delete_map', kwargs={'map_id': self.map.id}))
        self.assertEqual(resp.status_code, 302)

    def test_delete_map_owner_only(self):
        self.c.login(username='stranger@devforge.uz', password='pass123')
        resp = self.c.get(reverse('world_builder:delete_map', kwargs={'map_id': self.map.id}))
        self.assertEqual(resp.status_code, 404)

    def test_delete_map_success(self):
        self.c.login(username='builder@devforge.uz', password='pass123')
        resp = self.c.get(reverse('world_builder:delete_map', kwargs={'map_id': self.map.id}))
        self.assertEqual(resp.status_code, 302) # Redirect to dashboard
        self.assertFalse(WorldMap.objects.filter(id=self.map.id).exists())
