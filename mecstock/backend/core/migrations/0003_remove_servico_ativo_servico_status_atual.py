# Generated by Django 4.2 on 2025-05-21 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_endereco_complemento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servico',
            name='ativo',
        ),
        migrations.AddField(
            model_name='servico',
            name='status_atual',
            field=models.CharField(choices=[('Cadastrado', 'Cadastrado'), ('Aguardando Aprovação', 'Aguardando Aprovação'), ('Aprovado', 'Aprovado'), ('Em Andamento', 'Em Andamento'), ('Diagnóstico Adicional', 'Diagnóstico Adicional'), ('Aguardando Peças', 'Aguardando Peças'), ('Finalizado', 'Finalizado'), ('Entregue', 'Entregue'), ('Cancelado', 'Cancelado')], default='Cadastrado', max_length=50),
        ),
    ]
