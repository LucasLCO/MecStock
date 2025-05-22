from django.shortcuts import render
from rest_framework import viewsets
from .models import Cliente, Carro, Mecanico, Pagamento, Servico, Insumo, Endereco, Status
from .serializers import ClienteSerializer, CarroSerializer, MecanicoSerializer, PagamentoSerializer, ServicoSerializer, InsumoSerializer, EnderecoSerializer, StatusSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.response import Response

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class CarroViewSet(viewsets.ModelViewSet):
    queryset = Carro.objects.all()
    serializer_class = CarroSerializer

class MecanicoViewSet(viewsets.ModelViewSet):
    queryset = Mecanico.objects.all()
    serializer_class = MecanicoSerializer

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer

class ServicoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciamento de serviços.
    """
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer

    @swagger_auto_schema(
        operation_summary="Lista todos os serviços",
        operation_description="Retorna uma lista de todos os serviços cadastrados no sistema."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Detalha um serviço específico",
        operation_description="Retorna os detalhes completos de um serviço específico."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Cria um novo serviço",
        operation_description="Cria um novo serviço com os dados fornecidos."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Atualiza um serviço",
        operation_description="Atualiza todos os campos de um serviço existente."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Atualiza parcialmente um serviço",
        operation_description="Atualiza apenas os campos fornecidos de um serviço existente."
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Remove um serviço",
        operation_description="Remove permanentemente um serviço do sistema."
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_summary="Serviços ativos",
        operation_description="Retorna apenas os serviços que estão ativos no momento.",
        responses={200: ServicoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def ativos(self, request):
        """Filtra apenas serviços ativos."""
        ativos = self.queryset.filter(status_atual__in=[
            'Cadastrado', 'Aguardando Aprovação', 'Aprovado', 
            'Em Andamento', 'Diagnóstico Adicional', 'Aguardando Peças'
        ])
        serializer = self.get_serializer(ativos, many=True)
        return Response(serializer.data)

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

class EnderecoViewSet(viewsets.ModelViewSet):
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer