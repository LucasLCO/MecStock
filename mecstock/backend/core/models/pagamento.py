from django.db import models

class Pagamento(models.Model):
    pagamento_ID = models.AutoField(primary_key=True)
    valor_final = models.FloatField()
    valor_total = models.FloatField()
    metodo_pagamento = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"Pagamento {self.pagamento_ID} - {self.metodo_pagamento}"