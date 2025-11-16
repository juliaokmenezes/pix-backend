from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pagination import MyCustomPagination
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
    if request.method == "GET":
        accept = request.headers.get("Accept", "application/json") 
        if accept == "multipart/json":
            msgs = get_multiplas_mensagens(ispb)
            
        else: 
            msgs = get_ultima_mensagem(ispb)
        
        if not msgs:
            return JsonResponse({"mensagem"}, status=200)
        else:
            return JsonResponse({"mensagem"}, status=204)
        


class PixList(ListAPIView):
    queryset=Pix.objects.all()
    serializer_class = PixSerializer
    pagination_class = MyCustomPagination