from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    path('index/', views.IndexAnalitica.as_view(), name= 'analitica-index'),
<<<<<<< HEAD
    path('curva_base/', views.CurvaBaseView.as_view(), name='curva-base'),
=======
    path('curva_base/', views.CurvaBaseView.as_view(), name='curva-base')
>>>>>>> parent of 15158c48... cambios
]
