from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from expenses.models import Transaction, Category


class SummaryTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(username='alice', password='pass1234')
        cls.expense_cat = Category.objects.create(name='Food', type='expense', user=cls.alice)
        cls.income_cat = Category.objects.create(name='Salary', type='income', user=cls.alice)
    
    def setUp(self):
        self.client.force_authenticate(user=self.alice)
    
    def test_summary_with_transactions(self):
        Transaction.objects.create(user=self.alice, category=self.expense_cat, amount='500.00', date='2026-10-01')
        Transaction.objects.create(user=self.alice, category=self.expense_cat, amount='1000.00', date='2026-10-15')
        Transaction.objects.create(user=self.alice, category=self.income_cat, amount='5000.00', date='2026-10-31')

        response = self.client.get(reverse('transaction-summary'), {'date_from': '2026-10-01', 'date_to': '2026-10-31'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_income'], '5000.00')
        self.assertEqual(response.data['total_expense'], '1500.00')
        self.assertEqual(response.data['net'], '3500.00')
        self.assertEqual(response.data['transaction_count'], 3)

    def test_summary_empty_range_returns_zeros(self):

        response = self.client.get(reverse('transaction-summary'), {'date_from': '2026-10-01', 'date_to': '2026-10-31'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_income'], '0.00')
        self.assertEqual(response.data['total_expense'], '0.00')
        self.assertEqual(response.data['net'], '0.00')
        self.assertEqual(response.data['transaction_count'], 0)

    def test_monthly_breakdown(self):
        Transaction.objects.create(user=self.alice, category=self.expense_cat, amount='500.00', date='2026-10-01')
        Transaction.objects.create(user=self.alice, category=self.expense_cat, amount='1000.00', date='2026-10-15')
        Transaction.objects.create(user=self.alice, category=self.income_cat, amount='5000.00', date='2026-10-31')

        response = self.client.get(reverse('transaction-monthly'), {'year': '2026', 'month': '10'})
        self.assertEqual(response.status_code, 200)

        food_row = next(r for r in response.data['by_category'] if r['category'] == 'Food')
        self.assertEqual(food_row['total'], '1500.00')
        self.assertEqual(food_row['count'], 2)
        self.assertEqual(food_row['type'], 'expense')

        self.assertEqual(len(response.data['by_category']), 2)   # only 2 categories

        salary_row = next(r for r in response.data['by_category'] if r['category'] == 'Salary')
        self.assertEqual(salary_row['total'], '5000.00')
        self.assertEqual(salary_row['count'], 1)
        self.assertEqual(salary_row['type'], 'income')

    def test_monthly_missing_params_returns_400(self):
        response = self.client.get(reverse('transaction-monthly'), {'year': '2026'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)

    def test_monthly_invalid_month_returns_400(self):
        response = self.client.get(reverse('transaction-monthly'), {'year': '2026', 'month': '13'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('month', response.data)
