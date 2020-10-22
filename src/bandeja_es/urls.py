from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('index/', views.IndexView.as_view(), name= 'Bandejaeys'),
    path('paquete/crear/', views.CreatePaquete.as_view(), name='paquete-crear'),
    path('paquete/cargar/<pk>/', login_required(views.cargar_documentos), name='cargar-documentos' )
]
