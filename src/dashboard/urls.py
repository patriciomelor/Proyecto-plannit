from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.RootView.as_view(), name='root-screen'),
    path('accounts/profile/', views.ProfileView.as_view(), name='screen'),
    path('index/', views.EscritorioView.as_view(), name='index'),
    path('nuevo_usuario/', views.UsuarioView.as_view(), name='crear-usuario'),

]
