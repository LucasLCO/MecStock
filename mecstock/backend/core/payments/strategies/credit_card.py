from .base import PaymentStrategy

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, amount, card_details):
        if not self.validate_card(card_details):
            raise ValueError("Invalid credit card details")

        transaction_id = self.simulate_payment_processing(amount, card_details)
        return transaction_id

    def validate_card(self, card_details):
        return True

    def simulate_payment_processing(self, amount, card_details):
        return "txn_123456789"