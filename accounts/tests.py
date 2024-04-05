from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


class RegistrationAPITest(APITestCase):

    def test_registration(self):
        """ We create a new user and a valid Token is created upon successful registration of the user"""
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "secret_2024",
            "password2": "secret_2024"}
        response = self.client.post("/api/v1/dj-rest-auth/registration/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(get_user_model().objects.get().username, 'testuser')
        self.assertEqual(get_user_model().objects.get().email, 'testuser@example.com')

        self.user = get_user_model().objects.latest('id')
        self.token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['key'], self.token.key)



