from .base import PaymentStrategy

class BankTransferPayment(PaymentStrategy):
    def process_payment(self, amount, account_details):
        if not self.validate_account_details(account_details):
            raise ValueError("Invalid account details provided.")
        
        print(f"Processing bank transfer of {amount} to account {account_details['account_number']}")

        
        return {
            'status': 'success',
            'amount': amount,
            'account_number': account_details['account_number'],
            'transaction_id': 'BANK123456'
        }

    def validate_account_details(self, account_details):

        required_keys = ['account_number', 'bank_code']
        return all(key in account_details for key in required_keys) and isinstance(account_details['account_number'], str) and isinstance(account_details['bank_code'], str)