from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model    # для ссылки на активного пользователя
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient         # для имитации GET/POST запросов
from .models import Post
from .serializers import PostSerializer


class APIPostTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.admin = get_user_model().objects.create_superuser(
            username='admin',
            password='admin',
            )
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email',
            password='secret',
            )
        cls.post = Post.objects.create(
            author=cls.user,
            title='Title',
            body='Content',
        )

    # Testing Post model:
    def test_post_model_content(self):
        self.assertEqual(self.post.author.username, 'testuser')
        self.assertEqual(self.post.title, 'Title')
        self.assertEqual(self.post.body, 'Content')
        self.assertEqual(str(self.post), 'Title')

    # Testing views: (by simulating requests and checking responses):
    # For unauthenticated users:
    def test_get_posts_unauthenticated(self):
        # reverse - helps us to get url for this view from its name
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_posts_unauthenticated(self):
        response = self.client.post(reverse('post-list'), data={'title': 'First Post',
                                                                'body': 'Content'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_post_detail_unauthenticated(self):
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_post_detail_unauthenticated(self):
        response = self.client.delete(reverse('post-detail', kwargs={'pk': self.post.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # For authenticated users:
    def test_get_posts_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertContains(response, self.post)

    def test_post_posts_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('post-list'), data={'title': 'First Post',
                                                                'author': self.user.id,
                                                                'body': 'Content'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_post_detail_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.id}), format='json')
        no_response = self.client.get('api/v1/10000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(no_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('post-detail', kwargs={'pk': self.post.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get('post-list')
        # Check deleted successfully
        self.assertEqual(Post.objects.count(), 0)

        # For admin:
    def test_get_posts_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertContains(response, self.post)
        self.assertEqual(Post.objects.count(), 1)
        self.assertContains(response, self.post)

    def test_post_posts_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('post-list'), data={'title': 'First Post',
                                                                'author': self.user.id,
                                                                'body': 'Content'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_post_detail_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertContains(response, self.post)
        no_response = self.client.get('api/v1/10000')
        self.assertEqual(no_response.status_code, status.HTTP_404_NOT_FOUND)
