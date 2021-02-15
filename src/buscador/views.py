from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from django.contrib import messages
import os.path
import zipfile
from io import BytesIO
from django.conf import settings

from .filters import DocFilter
from panel_carga.models import Documento
from bandeja_es.models import Version, Paquete
# Create your views here.

class BuscadorIndex(ProyectoMixin, ListView):
    template_name = 'buscador/index.html'
    model = Documento
    context_object_name = 'documentos'
    

    def get_queryset(self):
        # qs = self.documentos_con_versiones()
        lista_documentos_filtrados = DocFilter(self.request.GET, queryset= documentos_con_versiones(self.request))
        return lista_documentos_filtrados.qs.order_by('Numero_documento_interno')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        paquetes = Paquete.objects.filter(version__in=versiones)
        lista_actual = []
        lista_final = []
        for version, paquete in zip(versiones, paquetes):
            lista_actual = [version, paquete]
            lista_final.append(lista_actual)
        print(lista_final)
        context['lista_final'] = lista_final
        # context['paquete'] = paquete
        return context
    
    def post(self, request, *args, **kwargs):
        listado_versiones_url = []
        doc = Documento.objects.get(pk=self.kwargs['pk'])
        versiones = Version.objects.filter(documento_fk=doc)
        for version in versiones:
            static = version.archivo.path
            listado_versiones_url.append(static)
        zip_subdir = "Documentos"
        zip_filename = "%s.zip" % zip_subdir
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w")
        for fpath in listado_versiones_url:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            zf.write(fpath, zip_path)
        zf.close()
        response = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

def documentos_con_versiones(request):
    eliminados_list = []
    qs =  Documento.objects.filter(proyecto=request.session.get('proyecto'))
    for doc in qs:
        version = Version.objects.filter(documento_fk=doc).exists()
        if not version:
            eliminados_list.append(doc.pk)

    queryset_final = Documento.objects.exclude(pk__in=eliminados_list).order_by('Especialidad')

    return queryset_final
    