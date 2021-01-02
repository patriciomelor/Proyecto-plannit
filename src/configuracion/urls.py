from django.urls import path, include
from . import views

urlpatterns = [
    path('listado/', views.UsuarioLista.as_view(), name='listar-usuarios'),
    path('nuevo_usuario/', views.UsuarioView.as_view(), name='crear-usuario'),
    path('editar_usuario/<pk>/', views.UsuarioEdit.as_view(), name='editar-usuario'),
    path('eliminar/<pk>/', views.UsuarioDelete.as_view(), name='eliminar-usuario'),
]
