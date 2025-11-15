from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import popular_banco, get_multiplas_mensagens, get_ultima_mensagem
import json
from .models import Pix

##acertar caminho URL
@csrf_exempt
def cadastro_pix(request, ispb, number):
    if request.method == "POST":
        popular_banco(ispb,number)
        return JsonResponse({"Pix Cadastrado com Sucesso"})
    
    return JsonResponse({"erro": "método não permitido"}, status=405)

@csrf_exempt
def recuperacao_mensagens(request, ispb):
    if request.method != "GET":
        return JsonResponse({"erro": "método não permitido"}, status=405)
    
    accept = request.headers.get("Accept", "").strip().lower()

    obter_mensagens = (
        get_multiplas_mensagens if accept == "multipart/json"
        else get_ultima_mensagem
    )

    msgs = obter_mensagens(ispb)

    if not msgs:
        return JsonResponse({"mensagem": None}, status=204)
    
    return JsonResponse({"mensagem": msgs}, status=200)

        



