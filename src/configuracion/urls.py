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
    path('proyecto-detalle/<pk>/', views.ProyectoDetail.as_view(), name='detalle-proyecto'),
    path('proyecto-editar/<pk>/', views.ProyectoEdit.as_view(), name='editar-proyecto'),
    path('proyecto-lista', views.ProyectoList.as_view(), name='lista-proyecto'),
    path('proyecto-delete/<pk>/', views.ProyectoDelete.as_view(), name='delete-proyecto'),
    path('proyecto-create/', views.ProyectoCreate.as_view(), name='crear-proyecto'),

]
