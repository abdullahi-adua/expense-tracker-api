from django.contrib.auth.models import User
from django.test import TestCase
from expenses.auth_serializers import RegisterSerializer


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