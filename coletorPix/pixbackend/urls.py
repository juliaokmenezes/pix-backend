from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from . import views

# router.register("pixapi", views.PixModelViewSet, basename="pix")

urlpatterns = [
    path('cadastro_pix/<int:ispb>/<int:xnumber/', views.cadastro_pix, name='cadastro_pix'),
    path("pixapi/", views.PixList.as_view())
]