from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.RootView.as_view(), name='root'),
    path('accounts/profile/', views.ProfileView.as_view(), name='screen'),
    path('index/', views.EscritorioView.as_view(), name='index'),
    path('borradores/', views.BorradorView.as_view(), name='Borradores'),

]
