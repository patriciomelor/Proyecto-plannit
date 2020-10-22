from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.RootView.as_view(), name='screen'),
    path('accounts/profile/', views.ProfileView.as_view(), name='screen'),
    path('index/', views.EscritorioView.as_view(), name='index'),
    path('bandejaeys/', views.BaesView.as_view(), name='Bandejaeys'),
    path('borradores/', views.BorradorView.as_view(), name='Borradores'),

]
