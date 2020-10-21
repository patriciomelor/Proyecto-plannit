from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.IndexView.as_view(), name= 'Bandejaeys'),
    path('paquete/crear/', views.CrearPaquete.as_view(), name='paquete-crear')
]
