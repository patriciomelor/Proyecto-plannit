from django.urls import path, include, register_converter, converters
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    path('recibidos/', views.InBoxView.as_view(), name= 'Bandejaeys'),
    path('enviados/', views.EnviadosView.as_view(), name= 'bandeja-enviados'),
    path('borradores/', views.BorradorList.as_view(), name= 'Borradores'),
    path('tramital/preview/', views.PrevPaqueteView.as_view(), name='paquete-preview'),
    path('version/nuevo/<paquete_pk>/', views.TablaPopupView.as_view(), name='nueva-version'),
    path('version/popup/<paquete_pk>/', views.PrevVersionView.as_view(), name='popup-version'),
    path('versiones/vue/<int:paquete_pk>/', login_required(views.vue_version), name='vue-version'),
    path('paquete/crear/<paquete_pk>/<versiones_pk>', login_required(views.create_paquete), name='paquete-crear'),
    path('paquete/detalle/<pk>/', views.PaqueteDetail.as_view(), name='paquete-detalle'),
    path('paquete/editar/<pk>/', views.PaqueteUpdate.as_view(), name='paquete-editar'),
    path('paquete/eliminar/<pk>/', views.PaqueteDelete.as_view(), name='paquete-eliminar'),
    path('borrador/crear/<borrador_pk>/', login_required(views.create_borrador), name='borrador-crear'),
    path('datos/', login_required(views.documentos_ajax), name='datos-baes'),


]
