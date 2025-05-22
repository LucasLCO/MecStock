class InvalidPaymentMethodException(Exception):
    """Exception raised for invalid payment method."""
    def __init__(self, method):
        self.method = method
        self.message = f"Invalid payment method: {self.method}"
        super().__init__(self.message)


class TransactionErrorException(Exception):
    """Exception raised for errors during payment transactions."""
    def __init__(self, transaction_id, message="Transaction error occurred"):
        self.transaction_id = transaction_id
        self.message = message
        super().__init__(self.message)