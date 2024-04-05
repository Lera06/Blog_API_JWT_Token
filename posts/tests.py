import json
from pytz import timezone as pytz_timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model    # для ссылки на активного пользователя
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from django_project import settings
from .models import Post
from .serializers import PostSerializer


class PostModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email',
            password='secret_2024',
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Title',
            body='Content',
            )

    def test_post_model_content(self):
        self.assertEqual(self.post.author.username, 'testuser')
        self.assertEqual(self.post.title, 'Title')
        self.assertEqual(self.post.body, 'Content')
        self.assertEqual(str(self.post), 'Title')


class PostAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email',
            password='secret_2024',
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Title',
            body='Content',
        )
        # We create a token to use it with a user
        self.token = Token.objects.create(user=self.user)
        # In order to authenticate ourselves we define a method:
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_read_posts_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('post-list'))    # reverse - helps us to get url for this view from its name
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertContains(response, self.post)

    def test_read_posts_un_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_read_post_detail_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Title')
        no_response = self.client.get('api/v1/10000')
        self.assertEqual(no_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_post_detail_un_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_by_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('post-detail', kwargs={'pk': 1}),
                                   {"author": 1,
                                    "title": 'Updated title',
                                    "body": 'Updated content',
                                    "created_at": self.post.created_at.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content),
                         {"id": 1,
                          "author": 1,
                          "title": "Updated title",
                          "body": "Updated content",
                          "created_at": self.post.created_at.astimezone(
                              pytz_timezone(settings.TIME_ZONE)).isoformat().replace(
                              "+00:00", "Z"),
                          })

    def test_update_post_by_random_user(self):
        self.random_user = get_user_model().objects.create_user(
            username='randomuser',
            email='randomuser@email',
            password='password_123',
        )
        self.client.force_authenticate(user=self.random_user)
        response = self.client.put(reverse('post-detail', kwargs={'pk': 1}),
                                   {"title": "New title",
                                    "body": "Content"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_by_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('post-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check deleted successfully
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_post_by_random_user(self):
        self.random_user = get_user_model().objects.create_user(
            username='randomuser2',
            email='randomuser2@email',
            password='password_345',
        )
        self.client.force_authenticate(user=self.random_user)
        response = self.client.delete(reverse('post-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('post-list'), data={'title': 'New Post',
                                                                'author': self.user.id,
                                                                'body': 'Content'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Post')
        self.assertEqual(response.data['author'], 1)

    def test_create_post_un_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('post-list'), data={'title': 'New Post',
                                                                'body': 'Content'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Testing Serializers (by creating instances and validating data):
class PostSerializerTest(APITestCase):

    @classmethod
    def setUp(cls):
        cls.user = get_user_model().objects.create_user(username='testuser',
                                                        email='test@email',
                                                        password='secret',)

        cls.post = Post.objects.create(author=cls.user,
                                       title='Title',
                                       body='Content',)

    def test_serializer_is_valid(self):
        data = {
                "id": self.post.id,
                "author": self.user.id,
                "title": self.post.title,
                "body": self.post.body,
                "created_at": self.post.created_at.isoformat()
            }
        serializer = PostSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    # We need to be sure that the serialized output matches the expected output:
    def test_serialized_output(self):
        serializer = PostSerializer(instance=self.post)
        expected_output = {
            "id": self.post.id,
            "author": self.user.id,
            "title": self.post.title,
            "body": self.post.body,
            "created_at": self.post.created_at.astimezone(pytz_timezone(settings.TIME_ZONE)).isoformat().replace(
                "+00:00", "Z"),
        }
        self.assertEqual(serializer.data, expected_output)






