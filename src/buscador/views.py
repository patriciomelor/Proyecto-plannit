from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from django.contrib import messages
from panel_carga.models import Documento
from bandeja_es.models import Version
# Create your views here.

class BuscadorIndex(ProyectoMixin, ListView):
    template_name = 'buscador/index.html'
    model = Documento
    paginate_by = 15
    context_object_name = 'documentos'
    
    def get_queryset(self):
        qs =  Documento.objects.filter(proyecto=self.proyecto)
        lista_documentos_filtrados = DocFilter(self.request.GET, queryset=qs)
        return  lista_documentos_filtrados.qs.order_by('Numero_documento_interno')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc = Documento.objects.filter(proyecto=self.proyecto)
        context["filter"] = DocFilter(self.request.GET, queryset=self.get_queryset())
        return context

class VersionesList(ProyectoMixin, DetailView):
    model = Documento
    template_name = 'buscador/detalle.html'
    context_object_name = 'documento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc = Documento.objects.get(pk=self.kwargs['pk'])
        versiones = Version.objects.filter(documento_fk=doc)
        context['versiones'] = versiones
        return context