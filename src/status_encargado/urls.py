from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.EncargadoIndex.as_view(), name='encargado-index'),
    path('index/', views.CreateTarea.as_view(), name='create-tarea'),
    path('index/', views.CreateRespuesta.as_view(), name='create-respuesta')
]
