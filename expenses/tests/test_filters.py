from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from expenses.models import Transaction, Category 


class TransactionFilterTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(username='alice', password='pass1234')
        cls.cat = Category.objects.create(name='Food', type='expense', user=cls.alice)
        cls.transport = Category.objects.create(name='Transport', type='expenses', user=cls.alice)
        cls.salary = Category.objects.create(name='salary', type='income', user=cls.alice)
    def setUp(self):
        self.client.force_authenticate(user=self.alice)
    
    def test_filter_by_date_from(self):
        # ARRANGE
        Transaction.objects.create(user=self.alice, category=self.cat, amount='50.00', date='2026-10-01')
        Transaction.objects.create(user=self.alice, category=self.cat, amount='75.00', date='2026-10-15')
        Transaction.objects.create(user=self.alice, category=self.cat, amount='100.00', date='2026-10-31')
        
        # ACT
        response = self.client.get(reverse('transaction-list'), {'date_from': '2026-10-15'})
        
        # ASSERT
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        for tx in response.data['results']:
            self.assertGreaterEqual(tx['date'], '2026-10-15')
    
    def test_filter_by_date_to(self):
        # ARRANGE
        Transaction.objects.create(user=self.alice, category=self.cat, amount='50.00', date='2026-10-01')
        Transaction.objects.create(user=self.alice, category=self.cat, amount='75.00', date='2026-10-15')
        Transaction.objects.create(user=self.alice, category=self.cat, amount='100.00', date='2026-10-31')
        
        # ACT
        response = self.client.get(reverse('transaction-list'), {'date_to': '2026-10-15'})
        
        # ASSERT
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        for tx in response.data['results']:
            self.assertLessEqual(tx['date'], '2026-10-15')
    
    def test_filter_by_date_range(self):
        # ARRANGE
        Transaction.objects.create(user=self.alice, category=self.cat, amount='50.00', date='2026-10-01')
        Transaction.objects.create(user=self.alice, category=self.cat, amount='75.00', date='2026-10-15')
        Transaction.objects.create(user=self.alice, category=self.cat, amount='100.00', date='2026-10-31')
        Transaction.objects.create(user=self.alice, category=self.cat, amount='100.00', date='2026-11-2')
        
        # ACT
        response = self.client.get(reverse('transaction-list'), {'date_from': '2026-10-15', 'date_to': '2026-11-2'})
        
        # ASSERT
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        for tx in response.data['results']:
            self.assertGreaterEqual(tx['date'], '2026-10-15')
            self.assertLessEqual(tx['date'], '2026-11-2')

    def test_filter_by_category(self):
        Transaction.objects.create(user=self.alice, category=self.cat, amount='50.00', date='2026-10-01')
        Transaction.objects.create(user=self.alice, category=self.transport, amount='75.00', date='2026-10-15')


        response = self.client.get(reverse('transaction-list'), {'category': self.cat.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['category']['id'], self.cat.id)

    def test_filter_by_type_expense(self):
        # ARRANGE
        Transaction.objects.create(user=self.alice, category=self.cat, amount='50.00', date='2026-10-01')
        Transaction.objects.create(user=self.alice, category=self.salary, amount='75.00', date='2026-10-15')
        
        # ACT
        response = self.client.get(reverse('transaction-list'), {'type': 'expense'})
        
        # ASSERT
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['type'], 'expense')

    def test_filter_backwards_date_range_returns_400(self):
        # ACT
        response = self.client.get(reverse('transaction-list'), {
            'date_from': '2026-10-31',
            'date_to': '2026-10-01',
        })
        
        # ASSERT
        self.assertEqual(response.status_code, 400)
        self.assertIn('date_to', response.data)