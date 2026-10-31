from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APITestCase
class LoginThrottleTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='alice', password='pass1234')

    def setUp(self):
        cache.clear()

    def test_login_throttled_after_five_attempts(self):
        """Login should be throttled after 5 attempts per minute."""
        # Real settings: login = '5/min'
        for i in range(5):
            response = self.client.post('/api/auth/login/', {
                'username': 'alice',
                'password': 'wrong-password',
            }, format='json')
            self.assertEqual(
                response.status_code, 401,
                f"Attempt {i+1} unexpectedly got {response.status_code}: {response.data}"
            )
        
        # 6th attempt → 429
        response = self.client.post('/api/auth/login/', {
            'username': 'alice',
            'password': 'wrong-password',
        }, format='json')
        self.assertEqual(
            response.status_code, 429,
            f"6th attempt should be throttled: got {response.status_code} {response.data}"
        )