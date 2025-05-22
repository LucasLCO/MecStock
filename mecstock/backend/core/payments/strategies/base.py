class PaymentStrategy:
    def pay(self, amount):
        raise NotImplementedError("This method should be overridden by subclasses")