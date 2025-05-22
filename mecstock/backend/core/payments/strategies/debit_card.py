from .base import PaymentStrategy

class DebitCardPayment(PaymentStrategy):
    def process_payment(self, amount, card_details):
        if not self.validate_card(card_details):
            raise ValueError("Invalid debit card details")
        
        print(f"Processing debit card payment of {amount} using card {card_details['card_number']}")
        
        return {
            'status': 'success',
            'amount': amount,
            'method': 'debit_card'
        }

    def validate_card(self, card_details):
        return 'card_number' in card_details and 'expiry_date' in card_details and 'cvv' in card_details