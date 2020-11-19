from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    path('index/', views.IndexAnalitica.as_view(), name= 'analitica-index'),
]
