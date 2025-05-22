from rest_framework import serializers
from .models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'amount', 'payment_method', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_payment_method(self, value):
        valid_methods = ['credit_card', 'debit_card', 'cash', 'bank_transfer', 'pix']
        if value not in valid_methods:
            raise serializers.ValidationError(f"Invalid payment method. Choose from: {', '.join(valid_methods)}.")
        return value