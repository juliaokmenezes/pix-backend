from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import popular_banco
import json
from .models import Pix

##acertar caminho URL
@csrf_exempt
def cadastro_pix(request, ispb, number):
    if request.method == "POST":
        popular_banco(ispb,number)
        return JsonResponse({"Pix Cadastrado com Sucesso"})
    
    return JsonResponse({"erro": "método não permitido"}, status=405)



