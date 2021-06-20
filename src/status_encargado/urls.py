from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.EncargadoIndex.as_view(), name='encargado-index'),
    path('crear_tarea/<doc_pk>/', views.CreateTarea.as_view(), name='create-tarea'),
    path('crear_respuesta/<task_pk>/', views.CreateRespuesta.as_view(), name='create-respuesta')
]
