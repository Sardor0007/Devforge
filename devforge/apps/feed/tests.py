from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Post, Comment, PostLike, Follow

User = get_user_model()

class FeedViewsTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user1 = User.objects.create_user(
            username='user1', email='user1@test.com', password='passuser123'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@test.com', password='passuser123'
        )
        self.post = Post.objects.create(
            author=self.user1,
            content="Hello DevForge!",
            post_type="text",
        )

    def test_feed_view_anonymous(self):
        resp = self.c.get(reverse('feed'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Hello DevForge!")

    def test_feed_view_authenticated(self):
        self.c.login(username='user1@test.com', password='passuser123')
        resp = self.c.get(reverse('feed'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Hello DevForge!")

    def test_post_create_view(self):
        self.c.login(username='user1@test.com', password='passuser123')
        resp = self.c.post(reverse('post_create'), {
            'content': 'This is a new test post',
            'post_type': 'text'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Post.objects.filter(content='This is a new test post').exists())

    def test_post_detail_view(self):
        self.c.login(username='user1@test.com', password='passuser123')
        resp = self.c.get(reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Hello DevForge!")

    def test_post_like_view(self):
        self.c.login(username='user2@test.com', password='passuser123')
        resp = self.c.post(reverse('post_like', kwargs={'pk': self.post.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(PostLike.objects.filter(user=self.user2, post=self.post).exists())

    def test_comment_add_view(self):
        self.c.login(username='user2@test.com', password='passuser123')
        resp = self.c.post(reverse('comment_add', kwargs={'pk': self.post.pk}), {
            'content': 'Cool post!'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Comment.objects.filter(post=self.post, author=self.user2, content='Cool post!').exists())

    def test_follow_toggle_view(self):
        self.c.login(username='user1@test.com', password='passuser123')
        resp = self.c.post(reverse('follow_toggle', kwargs={'username': 'user2'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())
