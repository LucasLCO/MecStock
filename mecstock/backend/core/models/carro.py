from django.db import models

class Carro(models.Model):
    carro_ID = models.AutoField(primary_key=True)
    modelo_carro = models.CharField(max_length=100)
    montadora = models.CharField(max_length=100)
    placa = models.CharField(max_length=10)
    combustivel = models.CharField(max_length=50)
    ano = models.IntegerField()
    Customer_ID = models.ForeignKey('Cliente', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.modelo_carro} - {self.montadora} ({self.ano})"