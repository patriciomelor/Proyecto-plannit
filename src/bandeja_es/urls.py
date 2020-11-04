from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('recibidos/', views.InBoxView.as_view(), name= 'Bandejaeys'),
    path('enviados/', views.EnviadosView.as_view(), name= 'bandeja-enviados'),
    path('booradores/', views.BorradorList.as_view(), name= 'Borradores'),
    path('papelera/', views.PapeleraView.as_view(), name= 'bandeja-papelera'),
    path('paquete/crear/', views.CreatePaqueteView.as_view(), name='paquete-crear'),
    path('paquete/detalle/<pk>/', views.PaqueteDetail.as_view(), name='paquete-detalle'),
    path('paquete/editar/<pk>/', views.PaqueteUpdate.as_view(), name='paquete-editar'),
    path('paquete/eliminar/<pk>/', views.PaqueteDelete.as_view(), name='paquete-eliminar'),
    # path('paquete/cargar/<int:pk>/', login_required(views.cargar_documentos), name='cargar-documentos' )
]
