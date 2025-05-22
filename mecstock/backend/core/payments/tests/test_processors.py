from django.test import TestCase
from core.payments.processors import PaymentProcessor
from core.payments.strategies.credit_card import CreditCardStrategy
from core.payments.strategies.debit_card import DebitCardStrategy
from core.payments.strategies.cash import CashStrategy
from core.payments.strategies.bank_transfer import BankTransferStrategy
from core.payments.strategies.pix import PixStrategy
from core.payments.exceptions import InvalidPaymentMethodException

class PaymentProcessorTests(TestCase):

    def setUp(self):
        self.processor = PaymentProcessor()

    def test_credit_card_payment(self):
        strategy = CreditCardStrategy()
        result = self.processor.process_payment(strategy, amount=100.0, card_details={'number': '4111111111111111', 'expiry': '12/25', 'cvv': '123'})
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Credit Card.')

    def test_debit_card_payment(self):
        strategy = DebitCardStrategy()
        result = self.processor.process_payment(strategy, amount=50.0, card_details={'number': '5111111111111118', 'expiry': '12/25', 'cvv': '123'})
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Debit Card.')

    def test_cash_payment(self):
        strategy = CashStrategy()
        result = self.processor.process_payment(strategy, amount=30.0)
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Cash.')

    def test_bank_transfer_payment(self):
        strategy = BankTransferStrategy()
        result = self.processor.process_payment(strategy, amount=200.0, account_details={'account_number': '123456', 'bank': 'Bank A'})
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Bank Transfer.')

    def test_pix_payment(self):
        strategy = PixStrategy()
        result = self.processor.process_payment(strategy, amount=75.0, pix_key='example@pix.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via PIX.')

    def test_invalid_payment_method(self):
        with self.assertRaises(InvalidPaymentMethodException):
            self.processor.process_payment(None, amount=100.0)