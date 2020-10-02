from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('export/', views.export_document, name='panel-export'),
    path('index/', views.import_document, name='PanelCarga'),
    path('seleccion/', views.ProyectoSelectView.as_view() , name="proyecto-select"),
    path('proyecto/lista/', login_required(views.ProyectoList.as_view()) , name="proyecto-lista"),
    path('proyecto/crear/', login_required(views.CreateProyecto.as_view()) , name="proyecto-crear"),
    path('proyecto/detalle/', login_required(views.DetailProyecto.as_view()) , name="proyecto-detalle"),
    path('documento/crear/', login_required(views.CreateDocumento.as_view()) , name="documento-crear"),
    path('documento/detalle/', login_required(views.DetailDocumento.as_view()) , name="documento-detalle"),

]
