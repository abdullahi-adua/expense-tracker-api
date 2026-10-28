from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from expenses.models import Category, Transaction


class TransactionCRUDTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(username='alice', password='pass1234')
        cls.bob = User.objects.create_user(username='bob', password='pass1234')
        cls.alice_cat = Category.objects.create(name='Food', type='expense', user=cls.alice)
        cls.bob_cat = Category.objects.create(name='Transport', type='expense', user=cls.bob)

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client.force_authenticate(user=self.alice)

    def test_create_transaction_with_own_category(self):
        """Alice can create a transaction with her own category."""
        response = self.client.post('/api/transactions/', {
            'category_id': self.alice_cat.id,
            'amount': '50.00',
            'date': '2026-10-28',
            'description': 'Lunch',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['category']['id'], self.alice_cat.id)
        self.assertEqual(Transaction.objects.get(id=response.data['id']).user, self.alice)

    def test_cannot_use_other_users_category(self):
        """Alice cannot create a transaction with Bob's category."""
        response = self.client.post('/api/transactions/', {
            'category_id': self.bob_cat.id,
            'amount': '50.00',
            'date': '2026-10-28',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category_id', response.data)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_list_only_own_transactions(self):
        """Alice sees only her own transactions."""
        Transaction.objects.create(
            user=self.alice, category=self.alice_cat,
            amount='10.00', date='2026-10-01', description='Alice',
        )
        Transaction.objects.create(
            user=self.bob, category=self.bob_cat,
            amount='20.00', date='2026-10-02', description='Bob',
        )
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_other_users_transaction_returns_404(self):
        """Alice cannot see Bob's transaction directly."""
        bob_tx = Transaction.objects.create(
            user=self.bob, category=self.bob_cat,
            amount='20.00', date='2026-10-02',
        )
        response = self.client.get(f'/api/transactions/{bob_tx.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_other_users_transaction(self):
        """Alice cannot delete Bob's transaction."""
        bob_tx = Transaction.objects.create(
            user=self.bob, category=self.bob_cat,
            amount='20.00', date='2026-10-02',
        )
        response = self.client.delete(f'/api/transactions/{bob_tx.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Transaction.objects.filter(id=bob_tx.id).exists())