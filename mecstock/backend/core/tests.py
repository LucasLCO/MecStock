from django.test import TestCase
from .models import Carro, Cliente, Endereco, Insumo, Mecanico, Pagamento, Servico, Status

class CarroModelTest(TestCase):
    def setUp(self):
        self.carro = Carro.objects.create(
            modelo_carro="Fusca",
            montadora="Volkswagen",
            placa="ABC-1234",
            combustivel="Gasolina",
            ano=1970,
            Customer_ID=1
        )

    def test_caro_creation(self):
        self.assertEqual(self.carro.modelo_carro, "Fusca")
        self.assertEqual(self.carro.montadora, "Volkswagen")
        self.assertEqual(self.carro.placa, "ABC-1234")
        self.assertEqual(self.carro.combustivel, "Gasolina")
        self.assertEqual(self.carro.ano, 1970)

class ClienteModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            Nome="Lucas",
            Email="lucas@example.com",
            CPF="123.456.789-00",
            Telefone="123456789",
            endereco_ID=1
        )

    def test_cliente_creation(self):
        self.assertEqual(self.cliente.Nome, "Lucas")
        self.assertEqual(self.cliente.Email, "lucas@example.com")

