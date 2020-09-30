from django.urls import path, include
from . import views

urlpatterns = [
    path('lista/', views.ProyectoList.as_view() , name="proyecto-lista"),
    path('crear/', views.CreateProyecto.as_view() , name="proyecto-crear"),
    path('detalle/', views.DetailProyecto.as_view() , name="proyecto-detalle"),
    path('documento/crear/', views.CreateDocumento.as_view() , name="documento-crear"),
    path('documento/detalle/', views.DetailDocumento.as_view() , name="documento-detalle"),

]
