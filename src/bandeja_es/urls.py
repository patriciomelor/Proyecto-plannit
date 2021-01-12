from django.urls import path, include, register_converter, converters
from django.contrib.auth.decorators import login_required
from . import views

class ListURLpks:
    regex = '[0-9]+'

    def to_python(self, value):
        return list(value)

    def to_url(self, value):
        val = list(value)
        return val

register_converter(ListURLpks, 'list')

urlpatterns = [
    path('recibidos/', views.InBoxView.as_view(), name= 'Bandejaeys'),
    path('enviados/', views.EnviadosView.as_view(), name= 'bandeja-enviados'),
    path('borradores/', views.BorradorList.as_view(), name= 'Borradores'),
    path('papelera/', views.PapeleraView.as_view(), name= 'bandeja-papelera'),
    path('paquete/preview/<borrador_pk>/', login_required(views.create_preview), name='paquete-preview'),
    path('paquete/preview2/<borrador_pk>/', views.CreatePaquete2.as_view(), name='paquete-preview2'),
    path('paquete/crear/<paquete_pk>/<versiones_pk>', login_required(views.create_paquete), name='paquete-crear'),
    path('paquete/detalle/<pk>/', views.PaqueteDetail.as_view(), name='paquete-detalle'),
    path('paquete/editar/<pk>/', views.PaqueteUpdate.as_view(), name='paquete-editar'),
    path('paquete/eliminar/<pk>/', views.PaqueteDelete.as_view(), name='paquete-eliminar'),
    path('borrador/crear/<borrador_pk>/', login_required(views.create_borrador), name='borrador-crear'),
    # path('paquete/cargar/<int:pk>/', login_required(views.cargar_documentos), name='cargar-documentos' )
    path('datos/', login_required(views.documentos_ajax), name='datos-baes'),
    path('datos2/', views.DocumentosSelect2.as_view(), name='datos-baes2'),
# Modals URL's
    path('modalcrear_version/', views.ModalPrevVersion.as_view(), name='modal-create-version'),
    path('modalcrear_paquete/', views.ModalPrevPaquete.as_view(), name='modal-create-paquete'),
    path('baes_modal/', views.BotonesForms.as_view(), name='botones-modal'),


]
