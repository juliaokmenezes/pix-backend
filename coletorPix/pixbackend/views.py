from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import popular_banco, get_multiplas_mensagens, get_ultima_mensagem, gerar_iteration_id
from .models import Pix, PixStream
import time

MAX_WAIT = 8  
CHECK_INTERVAL = 0.5  

@csrf_exempt
def cadastro_pix(request, ispb, number):
    if request.method == "POST":
        popular_banco(ispb, number)
        return JsonResponse({"mensagem": "Pix Cadastrado com Sucesso"})
    return JsonResponse({"erro": "método não permitido"}, status=405)



@csrf_exempt
def recuperacao_mensagens(request, ispb,  iterationId=None):
    if request.method != "GET":
        return JsonResponse({"erro": "método não permitido"}, status=405)

    accept = request.headers.get("Accept", "application/json")

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


    if iterationId is None:
        iterationId = gerar_iteration_id()
        PixStream.objects.create(
            ispb=ispb,
            iteration_id=iterationId,
            active=True
        )
    else:
        sessao = PixStream.objects.filter(
            ispb=ispb,
            iteration_id=iterationId,
            active=True
        ).first()
        if not sessao:
            return JsonResponse({"erro": "iterationId inválido ou sessão encerrada"}, status=404)

    status_code = 200 if msgs else 204

    response = JsonResponse({"mensagens": msgs}, status=status_code)
    response["Pull-Next"] = f"/api/pix/{ispb}/stream/{iterationId}"
    return response


@csrf_exempt
def stream_delete(request, ispb, iterationId):
    if request.method != "DELETE":
        return JsonResponse({"erro": "método não permitido"}, status=405)

    atual = PixStream.objects.filter(
        ispb=ispb, iteration_id=iterationId, active=True
    ).first()

    if not atual:
        return JsonResponse({"erro": "iterationId inválido ou já encerrado"}, status=404)

    atual.active = False
    atual.save()

    return JsonResponse({}, status=200)
