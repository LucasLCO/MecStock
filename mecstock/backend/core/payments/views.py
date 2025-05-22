from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import PaymentTransaction
from .serializers import PaymentTransactionSerializer
from .processors import PaymentProcessor
from .exceptions import InvalidPaymentMethodException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import PaymentService
from ..models import Pagamento, Servico

class PaymentViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = PaymentTransactionSerializer(data=request.data)
        if serializer.is_valid():
            payment_data = serializer.validated_data
            payment_method = payment_data.get('payment_method')
            processor = PaymentProcessor()

            try:
                transaction = processor.process_payment(payment_method, payment_data)
                return Response(PaymentTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
            except InvalidPaymentMethodException as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "Payment processing failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessPaymentView(APIView):
    def post(self, request):
        servico_id = request.data.get('servico_id')
        payment_method = request.data.get('payment_method')
        amount = request.data.get('amount')
        
        if not all([servico_id, payment_method, amount]):
            return Response(
                {"error": "Campos obrigatórios faltando"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            payment_service = PaymentService()
            payment_result, pagamento = payment_service.process_payment(
                servico_id=servico_id,
                payment_method=payment_method,
                amount=float(amount)
            )
            
            return Response({
                "status": payment_result['status'],
                "message": "Pagamento processado com sucesso",
                "payment_id": pagamento.pagamento_ID,
                "amount": amount,
                "method": payment_method
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Erro no processamento: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )