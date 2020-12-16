from django.urls import path, include
from . import views

urlpatterns = [
    path('nuevo_usuario/', views.UsuarioView.as_view(), name='crear-usuario'),
]
