import random
import string
from datetime import datetime, timedelta
from .models import Pix


def popular_banco(ispb, number):
    #atualizar para metodologia mais eficiente (concorrencia)
    for i in range(number):
        dados = geracao_dados(ispb)
        Pix.objects.create(**dados)


def geracao_dados(ispb):
    while True:
        end_to_end_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
        if not Pix.objects.filter(end_to_end_id=end_to_end_id).exists():
            break

    valor = round(random.uniform(1, 5000), 2)

    tx_id = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    campo_livre = ""
    data_hora_pagamento = datetime.now() - timedelta(minutes=random.randint(0, 9999))
    pagador_nome = random.choice(["Maria", "João", "Ana", "Carlos", "Beatriz", "Pedro"])
    pagador_cpf_cnpj = ''.join(random.choices(string.digits, k=11))
    pagador_ispb = ''.join(random.choices(string.digits, k=8))
    pagador_agencia = ''.join(random.choices(string.digits, k=4))
    pagador_conta_transacional = ''.join(random.choices(string.digits, k=8))
    pagador_tipo_conta = random.choice(["CC", "CP"])
    recebedor_nome = random.choice(["Loja 1", "Loja 2", "Loja 3", "Loja 4"])
    recebedor_cpf_cnpj = ''.join(random.choices(string.digits, k=11))
    recebedor_agencia = ''.join(random.choices(string.digits, k=4))
    recebedor_conta_transacional = ''.join(random.choices(string.digits, k=8))
    recebedor_tipo_conta = random.choice(["CC", "CP"])

    return {
        "end_to_end_id": end_to_end_id,
        "valor": valor,
        "tx_id": tx_id,
        "campo_livre": campo_livre,
        "data_hora_pagamento": data_hora_pagamento,
        "pagador_nome": pagador_nome,
        "pagador_cpf_cnpj": pagador_cpf_cnpj,
        "pagador_ispb": pagador_ispb,
        "pagador_agencia": pagador_agencia,
        "pagador_conta_transacional": pagador_conta_transacional,
        "pagador_tipo_conta": pagador_tipo_conta,
        "recebedor_nome": recebedor_nome,
        "recebedor_cpf_cnpj": recebedor_cpf_cnpj,
        "recebedor_ispb": ispb,
        "recebedor_agencia": recebedor_agencia,
        "recebedor_conta_transacional": recebedor_conta_transacional,
        "recebedor_tipo_conta": recebedor_tipo_conta,
    }

def get_ultima_mensagem(ispb):
    mensagem = Pix.objects.filter(
        recebedor_ispb=ispb,
        dado_visualizado=False
    ).order_by("data_hora_pagamento").first()
    
    if mensagem:
        Pix.objects.filter(id=mensagem.id).update(dado_visualizado=True)

    return mensagem

def get_multiplas_mensagens(ispb):
    mensagens = list(
        Pix.objects.filter(
            recebedor_ispb=ispb,
            dado_visualizado=False
        ).order_by("data_hora_pagamento")[:10]
    )

    ids = [msg.id for msg in mensagens]

    if ids:
        Pix.objects.filter(id__in=ids).update(dado_visualizado=True)

    return mensagens



def gerar_iteration_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
