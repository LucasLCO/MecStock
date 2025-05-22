from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Cliente, Carro, Pagamento, Mecanico, Servico

class ServicoTests(APITestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            Nome="John Doe",
            Email="john@example.com",
            CPF="12345678901",
            Telefone="1234567890",
            endereco_ID=1
        )
        self.carro = Carro.objects.create(
            modelo_carro="Fusca",
            montadora="Volkswagen",
            placa="ABC-1234",
            combustivel="Gasolina",
            ano=1970,
            Customer_ID=self.cliente.cliente_ID
        )
        self.pagamento = Pagamento.objects.create(
            valor_final=100.0,
            valor_total=100.0,
            metodo_pagamento="Cartão",
            status="Pago"
        )
        self.mecanico = Mecanico.objects.create(
            Nome="Jane Smith",
            Telefone="0987654321",
            Email="jane@example.com"
        )
        self.servico = Servico.objects.create(
            cliente_ID=self.cliente,
            carro_ID=self.carro,
            pagamento_ID=self.pagamento,
            mecanico_ID=self.mecanico,
            diagnostico="Troca de óleo",
            orcamento=150.0,
            descricao_servico="Troca de óleo e filtro",
            data_entrada="2023-01-01",
            data_saida="2023-01-02",
            retornado=False
        )

    def test_servico_creation(self):
        url = reverse('servico-list')
        data = {
            "cliente_ID": self.cliente.cliente_ID,
            "carro_ID": self.carro.carro_ID,
            "pagamento_ID": self.pagamento.pagamento_ID,
            "mecanico_ID": self.mecanico.mecanico_ID,
            "diagnostico": "Troca de pneus",
            "orcamento": 300.0,
            "descricao_servico": "Troca de pneus dianteiros",
            "data_entrada": "2023-01-03",
            "data_saida": "2023-01-04",
            "retornado": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_servico_list(self):
        url = reverse('servico-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_servico_detail(self):
        url = reverse('servico-detail', args=[self.servico.servico_ID])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descricao_servico'], self.servico.descricao_servico)