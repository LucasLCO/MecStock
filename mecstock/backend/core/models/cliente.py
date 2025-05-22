from django.db import models

class Cliente(models.Model):
    cliente_ID = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15)
    endereco_ID = models.ForeignKey('Endereco', on_delete=models.CASCADE)

    def __str__(self):
        return self.nome