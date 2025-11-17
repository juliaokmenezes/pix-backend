import time
import random
import string
from django.db import transaction
from .models import Pix, PixStream
from datetime import timedelta
from django.utils import timezone
from .utils import gerar_iteration_id

MAX_WAIT = 8
CHECK_INTERVAL = 0.5
MAX_STREAMS = 6
MULTIPART_LIMIT = 10

@transaction.atomic
def popular_banco(ispb, number):
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
    data_hora_pagamento = timezone.now() - timedelta(minutes=random.randint(0, 9999))
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


@transaction.atomic
def get_ultima_mensagem(ispb):
    mensagem = Pix.objects.select_for_update(skip_locked=True).filter(
        recebedor_ispb=ispb,
        dado_visualizado=False
    ).order_by("data_hora_pagamento").first()
    
    if mensagem:
        mensagem.dado_visualizado = True
        mensagem.save(update_fields=['dado_visualizado'])
    
    return mensagem


@transaction.atomic
def get_multiplas_mensagens(ispb, limit=10):

    mensagens = list(
        Pix.objects.select_for_update(skip_locked=True).filter(
            recebedor_ispb=ispb,
            dado_visualizado=False
        ).order_by("data_hora_pagamento")[:limit]
    )
    
    if mensagens:
        ids = [msg.id for msg in mensagens]
        Pix.objects.filter(id__in=ids).update(dado_visualizado=True)
    
    return mensagens


def buscar_mensagens_long_polling(ispb, accept):
    start_time = time.time()
    msgs = []

    while True:
        if accept == "multipart/json":
            msgs = get_multiplas_mensagens(ispb)
        else:
            msg = get_ultima_mensagem(ispb)
            msgs = [msg] if msg else []

        if msgs or (time.time() - start_time) >= MAX_WAIT:
            break

        time.sleep(CHECK_INTERVAL)

    return msgs

@transaction.atomic
def criar_ou_validar_stream(ispb, iterationId=None):
    if iterationId is None:
        active_streams = PixStream.objects.filter(ispb=ispb, ativo=True).count()
        if active_streams >= MAX_STREAMS:
            from django.http import JsonResponse
            return None, JsonResponse({
                "erro": f"Limite de coletores simultâneos atingido (máximo: {MAX_STREAMS})",
                "active_streams": active_streams
            }, status=429)

        iterationId = gerar_iteration_id()
        PixStream.objects.create(ispb=ispb, iteration_id=iterationId, ativo=True)
        return iterationId, None

    sessao = PixStream.objects.filter(ispb=ispb, iteration_id=iterationId, ativo=True).first()
    if not sessao:
        from django.http import JsonResponse
        return None, JsonResponse({
            "erro": "iterationId inválido ou sessão já encerrada"
        }, status=404)

    return iterationId, None