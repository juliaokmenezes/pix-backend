from django.db import models

class Pix(models.Model):
    end_to_end_id = models.CharField(max_length=50, unique=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tx_id = models.CharField(max_length=50)
    campo_livre = models.TextField(blank=True, null=True)
    data_hora_pagamento = models.DateTimeField()

    pagador_nome = models.CharField(max_length=100)
    pagador_cpf_cnpj = models.CharField(max_length=20)
    pagador_ispb = models.CharField(max_length=20)
    pagador_agencia = models.CharField(max_length=10)
    pagador_conta_transacional = models.CharField(max_length=20)
    pagador_tipo_conta = models.CharField(max_length=10)

    recebedor_nome = models.CharField(max_length=100)
    recebedor_cpf_cnpj = models.CharField(max_length=20)
    recebedor_ispb = models.CharField(max_length=20)
    recebedor_agencia = models.CharField(max_length=10)
    recebedor_conta_transacional = models.CharField(max_length=20)
    recebedor_tipo_conta = models.CharField(max_length=10)

    dado_visualizado = models.BooleanField(default=False)


class PixStream(models.Model):
    ispb = models.CharField(max_length=20)
    interation_id = models.CharField(max_length=50, unique=True)
    last_message_id = models.IntegerField(null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
