from django.urls import path, include
from . import views

urlpatterns = [
    path('crear/', views.CreateProyecto.as_view() , name="proyecto-crear"),
    path('detalle/', views.DetailProyecto.as_view() , name="proyect-detalle")
]
