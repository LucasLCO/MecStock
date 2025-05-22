from django.db import models

class Insumo(models.Model):
    insumo_ID = models.AutoField(primary_key=True)
    preco = models.FloatField()
    qtd = models.IntegerField()
    nome = models.CharField(max_length=255)
    descricao = models.TextField()

    def __str__(self):
        return self.nome