from django.contrib import admin
from .models import Pix, PixStream

@admin.register(Pix)
class PixAdmin(admin.ModelAdmin):
    list_display = ("end_to_end_id", "valor", "recebedor_nome", "recebedor_ispb", "dado_visualizado", "data_hora_pagamento")
    list_filter = ("recebedor_ispb", "dado_visualizado")
    search_fields = ("end_to_end_id", "pagador_nome", "recebedor_nome", "tx_id")

@admin.register(PixStream)
class PixStreamAdmin(admin.ModelAdmin):
    list_display = ("iteration_id", "ispb", "ativo", "criacao")
    list_filter = ("ativo",)
    search_fields = ("iteration_id", "ispb")
