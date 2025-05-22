from django.test import TestCase
from ..models import PaymentTransaction
from ..exceptions import InvalidPaymentMethodException

class PaymentTransactionModelTest(TestCase):
    def setUp(self):
        self.transaction = PaymentTransaction.objects.create(
            amount=100.00,
            method='credit_card',
            status='pending'
        )

    def test_payment_transaction_creation(self):
        self.assertEqual(self.transaction.amount, 100.00)
        self.assertEqual(self.transaction.method, 'credit_card')
        self.assertEqual(self.transaction.status, 'pending')

    def test_invalid_payment_method(self):
        with self.assertRaises(InvalidPaymentMethodException):
            PaymentTransaction.objects.create(
                amount=50.00,
                method='invalid_method',
                status='pending'
            )

    def test_payment_transaction_status_update(self):
        self.transaction.status = 'completed'
        self.transaction.save()
        self.assertEqual(self.transaction.status, 'completed')

    def test_payment_transaction_str(self):
        self.assertEqual(str(self.transaction), f'Transaction {self.transaction.id}: {self.transaction.amount} - {self.transaction.method}')