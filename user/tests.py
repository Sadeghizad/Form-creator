# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User


class UserRegistrationTest(APITestCase):
    def test_user_registration(self):
        url = reverse('registration-list')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'phone_number': '09123456789',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

class UserLoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123',
            phone_number='09123456789'
        )

    def test_login_with_username(self):
        url = reverse('custom_login')
        data = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_email(self):
        url = reverse('custom_login')
        data = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_phone_number(self):
        url = reverse('custom_login')
        data = {
            'phone_number': '09123456789',
            'password': 'TestPassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
