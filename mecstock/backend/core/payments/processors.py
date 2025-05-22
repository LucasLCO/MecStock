from .strategies.cash import CashPaymentStrategy
from .strategies.credit_card import CreditCardPaymentStrategy
from .strategies.debit_card import DebitCardPaymentStrategy
from .strategies.bank_transfer import BankTransferPaymentStrategy
from .strategies.pix import PixPaymentStrategy

class PaymentProcessor:
    def __init__(self):
        self.strategies = {
            'cash': CashPaymentStrategy(),
            'credit_card': CreditCardPaymentStrategy(),
            'debit_card': DebitCardPaymentStrategy(),
            'bank_transfer': BankTransferPaymentStrategy(),
            'pix': PixPaymentStrategy()
        }
    
    def process_payment(self, payment_method, amount, **kwargs):
        """
        Process a payment using the specified payment method
        
        Args:
            payment_method (str): The payment method (cash, credit_card, etc.)
            amount (float): The payment amount
            **kwargs: Additional arguments needed for specific payment methods
            
        Returns:
            dict: Payment result
            
        Raises:
            ValueError: If payment method is not supported
        """
        if payment_method not in self.strategies:
            raise ValueError(f"Unsupported payment method: {payment_method}")
            
        strategy = self.strategies[payment_method]
        return strategy.process_payment(amount, **kwargs)