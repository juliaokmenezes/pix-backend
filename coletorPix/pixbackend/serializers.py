from rest_framework import serializers
from .models import Pix

class PixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pix
        fields = [
            "id",
            "end_to_end_id",
            "valor",
            "tx_id",
            "campo_livre",
            "data_hora_pagamento",

            "pagador_nome",
            "pagador_cpf_cnpj",
            "pagador_ispb",
            "pagador_agencia",
            "pagador_conta_transacional",
            "pagador_tipo_conta",

            "recebedor_nome",
            "recebedor_cpf_cnpj",
            "recebedor_ispb",
            "recebedor_agencia",
            "recebedor_conta_transacional",
            "recebedor_tipo_conta",

            "dado_visualizado"
        ]
