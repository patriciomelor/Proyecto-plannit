from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.RootView.as_view(), name='screen'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('escritorio/', views.EscritorioView.as_view(), name='Escritorio'),
    path('paneldecarga/',views.PdcView.as_view(), name='PanelCarga'),
]
