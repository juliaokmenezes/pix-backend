from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import popular_banco, get_multiplas_mensagens, get_ultima_mensagem, gerar_iteration_id
import json
from .models import Pix, PixStream

##acertar caminho URL
@csrf_exempt
def cadastro_pix(request, ispb, number):
    if request.method == "POST":
        popular_banco(ispb,number)
        return JsonResponse({"Pix Cadastrado com Sucesso"})
    
    return JsonResponse({"erro": "método não permitido"}, status=405)

@csrf_exempt
def recuperacao_mensagens(request, ispb):
    if request.method == "GET":
        accept = request.headers.get("Accept", "application/json") 
        
        if accept == "multipart/json":
            msgs = get_multiplas_mensagens(ispb)   
        else: 
            msg = get_ultima_mensagem(ispb)        
            msgs = [msg] if msg else []            
        
        iteration = gerar_iteration_id()

        PixStream.objects.create(
            ispb=ispb,
            iteration_id=iteration,
            active=True
        )

        status_code = 200 if msgs else 204

        response = JsonResponse(
            {"mensagens": msgs},
            status=status_code
        )

        response["Pull-Next"] = f"/api/pix/{ispb}/stream/{iteration}"

        return response
    
    return JsonResponse({"erro": "método não permitido"}, status=405)

