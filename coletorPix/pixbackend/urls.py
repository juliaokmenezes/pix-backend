from django.urls import path
from . import views

urlpatterns = [
    path("api/util/msgs/<str:ispb>/<int:number>", views.cadastro_pix, name='cadastro_pix'),
    path("api/pix/<str:ispb>/stream/start", views.recuperacao_mensagens, name='pix_stream_start'),
    path("api/pix/<str:ispb>/stream/<str:iterationId>", views.recuperacao_mensagens, name='pix_stream_continuation'),
    path("api/pix/<str:ispb>/stream/<str:iterationId>/delete", views.stream_delete, name='pix_stream_delete'),

]