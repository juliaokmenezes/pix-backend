from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .service import (
    popular_banco,
    buscar_mensagens_long_polling,
    criar_ou_validar_stream
)
from .serializers import serializar_mensagens


MAX_WAIT = 8
CHECK_INTERVAL = 0.5
MAX_STREAMS = 6
MULTIPART_LIMIT = 10


@csrf_exempt
def cadastro_pix(request, ispb, number):
    if request.method != "POST":
        return JsonResponse({"erro": "método não permitido"}, status=405)

    popular_banco(ispb, number)
    return JsonResponse({"mensagem": "Pix Cadastrado com Sucesso"})


@csrf_exempt
@transaction.atomic
def recuperacao_mensagens(request, ispb, iterationId=None):
    if request.method != "GET":
        return JsonResponse({"erro": "método não permitido"}, status=405)

    accept = request.headers.get("Accept", "application/json")
    iterationId, erro_response = criar_ou_validar_stream(ispb, iterationId)
    if erro_response:
        return erro_response

    msgs = buscar_mensagens_long_polling(ispb, accept)

    status_code = 200 if msgs else 204
    response = JsonResponse({"mensagens": serializar_mensagens(msgs)}, status=status_code)
    response["Pull-Next"] = f"/api/pix/{ispb}/stream/{iterationId}"
    return response


@csrf_exempt
@transaction.atomic
def stream_delete(request, ispb, iterationId):
    if request.method != "DELETE":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    from .models import PixStream

    sessao = PixStream.objects.filter(ispb=ispb, iteration_id=iterationId, ativo=True).first()
    if not sessao:
        return JsonResponse({"erro": "iterationId inválido ou sessão já encerrada"}, status=404)

    sessao.ativo = False
    sessao.save(update_fields=['ativo'])
    return JsonResponse({"mensagem": "Stream encerrado com sucesso", "iterationId": iterationId}, status=200)