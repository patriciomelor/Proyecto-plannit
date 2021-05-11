from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.RootView.as_view(), name='root-screen'),
    path('accounts/profile/', views.ProfileView.as_view(), name='screen'),
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    path('index/', views.EscritorioView.as_view(), name='index'),

]
