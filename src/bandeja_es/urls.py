from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('index/', views.IndexView.as_view(), name= 'Bandejaeys'),
    path('paquete/crear/', login_required(views.create_paquete), name='paquete-crear'),
]
