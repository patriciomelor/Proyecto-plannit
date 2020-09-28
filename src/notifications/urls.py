from django.urls import path, include
from . import views

urlpatterns = [
    path('listado/', views.NotificacionList.as_view() , name="noti-list")
]
