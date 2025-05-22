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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
    """
    Endpoint para processamento de pagamentos.
    Utiliza o padrão Strategy para lidar com diferentes métodos de pagamento.
    """

    @swagger_auto_schema(
        operation_summary="Processa um pagamento",
        operation_description="""
        Processa um pagamento para um serviço utilizando o método especificado.
        Implementa o padrão Strategy para suportar diferentes processadores de pagamento.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['servico_id', 'payment_method', 'amount'],
            properties={
                'servico_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do serviço'),
                'payment_method': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Método de pagamento',
                    enum=['cash', 'credit_card', 'debit_card', 'bank_transfer', 'pix']
                ),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Valor do pagamento')
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status do pagamento'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensagem de sucesso'),
                    'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do pagamento'),
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Valor pago'),
                    'method': openapi.Schema(type=openapi.TYPE_STRING, description='Método utilizado')
                }
            ),
            400: 'Parâmetros inválidos',
            404: 'Serviço não encontrado',
            500: 'Erro no processamento do pagamento'
        }
    )
    def post(self, request):
        # Extract data from request
        servico_id = request.data.get('servico_id')
        payment_method = request.data.get('payment_method')
        amount = request.data.get('amount')
        
        # Validate input
        if not all([servico_id, payment_method, amount]):
            return Response(
                {"error": "Campos obrigatórios faltando"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Process the payment using our service
            payment_service = PaymentService()
            payment_result, pagamento = payment_service.process_payment(
                servico_id=servico_id,
                payment_method=payment_method,
                amount=float(amount)
            )
            
            # Return the result
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