from django.contrib.auth.models import User
from django.test import TestCase
from expenses.auth_serializers import RegisterSerializer
from rest_framework import status
from rest_framework.test import APITestCase



class RegisterSerializerTest(TestCase):
    def test_creates_user_with_hashed_password(self):
        serializer = RegisterSerializer(data={
            'username': 'alice',
            'email': 'alice@example.com',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'password': 'Str0ng-Pass-2026',
            'password_confirm': 'Str0ng-Pass-2026',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        
        # User exists
        self.assertEqual(user.username, 'alice')
        self.assertEqual(user.email, 'alice@example.com')
        self.assertEqual(user.first_name, 'Alice')
        self.assertEqual(user.last_name, 'Smith')
        
        # Password is hashed, not plaintext
        self.assertNotEqual(user.password, 'Str0ng-Pass-2026')
        self.assertTrue(user.password.startswith('pbkdf2_') or user.password.startswith('argon2'))
        
        # Password verifies
        self.assertTrue(user.check_password('Str0ng-Pass-2026'))

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username='existing', email='alice@example.com',
            password='Str0ng-Pass-2026',
        )
        serializer = RegisterSerializer(data={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Str0ng-Pass-2026',
            'password_confirm': 'Str0ng-Pass-2026',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class JWTFlowTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="alice", password="password123")
    
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_login_with_valid_credentials_returns_tokens(self):

        response = self.client.post(f'/api/auth/login/', {
            "username": "alice",
            "password": "password123"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_invalid_credentials_returns_401(self):
        response = self.client.post(f'/api/auth/login/', {
                    "username": "alice",
                    "password": "Password"
                }, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED )

    def test_refresh_with_valid_token_returns_new_access(self):
        login_response = self.client.post('/api/auth/login/', {
            "username": "alice",
            "password": "password123",
        }, format='json')
        refresh_token = login_response.data['refresh']
        
        response = self.client.post('/api/auth/refresh/', {
            "refresh": refresh_token,
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_refresh_with_invalid_token_returns_401(self):
        response = self.client.post('/api/auth/refresh/', {
            "refresh": "not-a-valid-token",
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_without_token_returns_401(self):
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_with_valid_token_returns_200(self):
        login_response = self.client.post('/api/auth/login/', {
            "username": "alice",
            "password": "password123",
        }, format='json')
        access_token = login_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/transactions/')
        
        self.assertEqual(response.status_code, 200)