from .base import PaymentStrategy

class CashPaymentStrategy(PaymentStrategy):
    def process_payment(self, amount):
        # Logic for processing cash payment
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        
        # Simulate cash payment processing
        print(f"Processing cash payment of ${amount:.2f}")
        return {
            "status": "success",
            "amount": amount,
            "method": "cash"
        }