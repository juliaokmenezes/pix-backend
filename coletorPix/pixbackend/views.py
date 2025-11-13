from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import geracao_dados
import json
from .models import Pix

@csrf_exempt
def cadastro_pix(request, ispb, x):
    if request.method == "POST":
        resultado = geracao_dados(ispb,x)
        return JsonResponse({"resultado": resultado})
    
    return JsonResponse({"erro": "método não permitido"}, status=405)

