from django.urls import path
from .payments.views import ProcessPaymentView

urlpatterns = [
    path('api/process-payment/', ProcessPaymentView.as_view(), name='process-payment'),
]