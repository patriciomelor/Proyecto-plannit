from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView, View
from panel_carga.views import ProyectoMixin

from .models import Proyecto, Documento, Revision, Historial

# Create your views here.

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

class RootView(RedirectView):
    pattern_name = 'account_login'

class IndexView(ProyectoMixin, TemplateView):
    template_name = "index-base.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proyecto"] = self.proyecto
        return context
    

class EscritorioView(ProyectoMixin, TemplateView):
    template_name = "administrador/Escritorio/dash.html"


class BaesView(ProyectoMixin, TemplateView):
    template_name = "administrador/BandejaEyS/baes.html"

    # OPCION 1
    # select Documento.num_docuemto, Documento.nombre, Documento.owner, documento.emision.estado_contratista, Historial.fecha
    # from Docuemto, Historial
    # when (documento.pk == Historial.documento)

    # OPCION 2
    # select Documento.num_docuemto, Documento.nombre, Documento.owner, Revision.estado_contratista, Historial.fecha
    # from Docuemto, Revision, Historial
    # when (documento.pk == Historial.documento) and (documento.pk == Revision.documento)





class BorradorView(ProyectoMixin, TemplateView):
    template_name = "administrador/Borradores/borrador.html"

