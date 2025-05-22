from django.test import TestCase
from ..strategies.credit_card import CreditCardPayment
from ..strategies.debit_card import DebitCardPayment
from ..strategies.cash import CashPayment
from ..strategies.bank_transfer import BankTransferPayment
from ..strategies.pix import PixPayment
from ..exceptions import InvalidPaymentMethodException

class PaymentStrategyTests(TestCase):

    def setUp(self):
        self.credit_card_payment = CreditCardPayment()
        self.debit_card_payment = DebitCardPayment()
        self.cash_payment = CashPayment()
        self.bank_transfer_payment = BankTransferPayment()
        self.pix_payment = PixPayment()

    def test_credit_card_payment(self):
        result = self.credit_card_payment.process(amount=100.0, card_info={'number': '4111111111111111', 'expiry': '12/25', 'cvv': '123'})
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Credit Card.')

    def test_debit_card_payment(self):
        result = self.debit_card_payment.process(amount=50.0, card_info={'number': '5500000000000004', 'expiry': '12/25', 'cvv': '123'})
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Debit Card.')

    def test_cash_payment(self):
        result = self.cash_payment.process(amount=20.0)
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Cash.')

    def test_bank_transfer_payment(self):
        result = self.bank_transfer_payment.process(amount=200.0, account_info={'account_number': '123456', 'bank_code': '001'})
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via Bank Transfer.')

    def test_pix_payment(self):
        result = self.pix_payment.process(amount=75.0, pix_key='example@pix.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Payment processed successfully via PIX.')

    def test_invalid_payment_method(self):
        with self.assertRaises(InvalidPaymentMethodException):
            self.credit_card_payment.process(amount=100.0, card_info=None)  # Simulating invalid input for credit card payment