from django.db import models

class Servico(models.Model):
    # Status choices for dropdown
    STATUS_CHOICES = [
        ('Cadastrado', 'Cadastrado'),
        ('Aguardando Aprovação', 'Aguardando Aprovação'),
        ('Aprovado', 'Aprovado'),
        ('Em Andamento', 'Em Andamento'),
        ('Diagnóstico Adicional', 'Diagnóstico Adicional'),
        ('Aguardando Peças', 'Aguardando Peças'),
        ('Finalizado', 'Finalizado'),
        ('Entregue', 'Entregue'),
        ('Cancelado', 'Cancelado'),
    ]
    
    servico_ID = models.AutoField(primary_key=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    carro = models.ForeignKey('Carro', on_delete=models.CASCADE)
    diagnostico = models.TextField()
    orcamento = models.FloatField()
    pagamento = models.ForeignKey('Pagamento', on_delete=models.CASCADE)
    descricao_servico = models.TextField()
    data_entrada = models.DateField()
    data_saida = models.DateField()
    retornado = models.BooleanField(default=False)
    mecanico = models.ForeignKey('Mecanico', on_delete=models.CASCADE)
    status_atual = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Cadastrado')
    # Add the home service fields
    home_service = models.BooleanField(default=False)
    service_address = models.ForeignKey('Endereco', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='servicos_realizados',
                                       help_text="Endereço onde o serviço será realizado (apenas para serviços domiciliares)")

    def __str__(self):
        return f'Serviço {self.servico_ID} - Cliente {self.cliente.nome}'