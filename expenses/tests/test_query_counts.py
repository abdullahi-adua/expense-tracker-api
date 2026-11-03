from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from expenses.models import Transaction, Category
from django.urls import reverse


class QueryCountTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(username='alice', password='pass1234')
        cls.cat = Category.objects.create(name='Food', type='expense', user=cls.alice)
       
        for i in range(5):
            Transaction.objects.create(
                user=cls.alice, category=cls.cat,
                amount='50.00', date='2026-10-01',
            )
    
    def setUp(self):
        self.client.force_authenticate(user=self.alice)
    
    def test_transaction_list_query_count(self):
        
        with self.assertNumQueries(2):
            response = self.client.get(reverse('transaction-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_transaction_detail_query_count(self):
        
        tx = Transaction.objects.first()
        with self.assertNumQueries(1):
            response = self.client.get(reverse('transaction-detail', args=[tx.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_summary_query_count(self):
        
        with self.assertNumQueries(3):   
            response = self.client.get(reverse('transaction-summary'), {
                'date_from': '2026-10-01', 'date_to': '2026-10-31',
            })
        self.assertEqual(response.status_code, 200)
    
    def test_monthly_query_count(self):
        
        with self.assertNumQueries(1):
            response = self.client.get(reverse('transaction-monthly'), {
                'year': '2026', 'month': '10',
            })
        self.assertEqual(response.status_code, 200)