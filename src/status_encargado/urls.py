from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.EncargadoIndex.as_view(), name='status-index')
]
