from django.urls import path, include, register_converter, converters
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('filtro/', views.BuscadorIndex.as_view() , name='buscador-index'),
    path('lista_versiones/<pk>/', views.VersionesList.as_view() , name='buscador-detalle'),
]
