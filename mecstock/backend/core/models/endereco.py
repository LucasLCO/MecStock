from django.db import models

class Endereco(models.Model):
    endereco_ID = models.AutoField(primary_key=True)
    cep = models.CharField(max_length=10)
    rua = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=15)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    complemento = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.rua}, {self.numero}, {self.complemento+', ' if self.complemento else ''}{self.bairro}, {self.cidade} - {self.estado}"