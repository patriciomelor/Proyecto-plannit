from django.urls import path, include
from . import views

urlpatterns = [
    path('index_admin/', views.EncargadoIndex.as_view(), name='encargado-index'),
    path('graph_admin/', views.EncargadoGraficoView.as_view(), name='encargado-grafico'),
    path('index_rev/', views.RevisorView.as_view(), name='revisor-index'),
    path('rev_sent/', views.RevisorSentView.as_view(), name='revisor-sent'),
    path('detail_tarea/<pk>/', views.TareaDetailView.as_view(), name='detail-tarea'),
    path('crear_tarea/<doc_pk>/', views.CreateTarea.as_view(), name='create-tarea'),
    path('crear_respuesta/<task_pk>/', views.CreateRespuesta.as_view(), name='create-respuesta')
]
