from django.urls import path
from . import views

urlpatterns = [
    path('cadastro_pix/<int:ispb>/<int:x>/', views.cadastro_pix, name='cadastro_pix'),
]