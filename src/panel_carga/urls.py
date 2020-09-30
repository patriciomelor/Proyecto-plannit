from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('lista/', login_required(views.ProyectoList.as_view()) , name="proyecto-lista"),
    path('crear/', login_required(views.CreateProyecto.as_view()) , name="proyecto-crear"),
    path('detalle/', login_required(views.DetailProyecto.as_view()) , name="proyecto-detalle"),
    path('documento/crear/', login_required(views.CreateDocumento.as_view()) , name="documento-crear"),
    path('documento/detalle/', login_required(views.DetailDocumento.as_view()) , name="documento-detalle"),

]
