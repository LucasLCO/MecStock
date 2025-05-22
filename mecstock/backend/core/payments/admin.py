from django.contrib import admin
from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'method', 'status', 'created_at')
    search_fields = ('method', 'status')
    list_filter = ('method', 'status')
    ordering = ('-created_at',)