from django.urls import path
from . import views

urlpatterns = [
    path('cadastro_pix/<int:ispb>/<int:xnumber/', views.cadastro_pix, name='cadastro_pix'),
    path("api/pix/<str:ispb>/stream/start", views.recuperacao_mensagens),
    path("api/pix/<str:ispb>/stream/<str:iterationId>", views.recuperacao_mensagens),
    path("api/pix/<str:ispb>/stream/<str:iterationId>", views.stream_delete),

]