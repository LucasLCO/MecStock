from .base import PaymentStrategy

class PixPaymentStrategy(PaymentStrategy):
    def process_payment(self, amount, account_info):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        
        transaction_id = self._generate_transaction_id()
        success = self._mock_pix_api_call(amount, account_info)
        
        if success:
            return {
                "transaction_id": transaction_id,
                "status": "success",
                "amount": amount,
                "method": "PIX"
            }
        else:
            raise Exception("Payment processing failed.")

    def _generate_transaction_id(self):
        import random
        return f"PIX-{random.randint(1000, 9999)}"

    def _mock_pix_api_call(self, amount, account_info):
        return True