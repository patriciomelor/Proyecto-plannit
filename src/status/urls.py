from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.StatusIndex.as_view(), name='status-index')
]
