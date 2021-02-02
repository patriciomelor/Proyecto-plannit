from django.urls import path, include
from . import views

urlpatterns = [
    #URL DE USUARIOS
    path('listado-user/', views.UsuarioLista.as_view(), name='listar-usuarios'),
    path('nuevo-user/', views.UsuarioView.as_view(), name='crear-usuario'),
    path('editar-user/<pk>/', views.UsuarioEdit.as_view(), name='editar-usuario'),
    path('eliminar-user/<pk>/', views.UsuarioDelete.as_view(), name='eliminar-usuario'),
    path('detalle-user/<pk>/', views.UsuarioDetail.as_view(), name ='detalle-usuario'),
    #URL DE PROYECTOS
    path('proyecto-detalle', views.ProyectoDetail, name='detalle-proyecto'),
    path('proyecto-editar', views.ProyectoEdit, name='editar-proyecto'),
    path('proyecto-lista', views.ProyectoList, name='lista-proyecto'),
    path('proyecto-delete', views.ProyectoDelete, name='delete-proyecto'),

]
