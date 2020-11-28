from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('recibidos/', views.InBoxView.as_view(), name= 'Bandejaeys'),
    path('enviados/', views.EnviadosView.as_view(), name= 'bandeja-enviados'),
    path('borradores/', views.BorradorList.as_view(), name= 'Borradores'),
    path('papelera/', views.PapeleraView.as_view(), name= 'bandeja-papelera'),
    path('paquete/crear/', login_required(views.create_paquete), name='paquete-crear'),
    path('paquete/detalle/<pk>/', views.PaqueteDetail.as_view(), name='paquete-detalle'),
    path('paquete/editar/<pk>/', views.PaqueteUpdate.as_view(), name='paquete-editar'),
    path('paquete/eliminar/<pk>/', views.PaqueteDelete.as_view(), name='paquete-eliminar'),
    path('paquete/crear/func/', login_required(views.create_paquete), name='paquete-crear'),
    path('borrador/crear/', login_required(views.create_borrador), name='borrador-crear'),

    
    # path('paquete/cargar/<int:pk>/', login_required(views.cargar_documentos), name='cargar-documentos' )
]
