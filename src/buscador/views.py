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
        first_v_date = versiones.first().fecha
        last_v_date = versiones.last().fecha
        delta_date = abs((last_v_date - first_v_date).days)
        paquetes = Paquete.objects.filter(version__in=versiones)
        lista_actual = []
        lista_final = []
        for version, paquete in zip(versiones, paquetes):
            lista_actual = [version, paquete]
            lista_final.append(lista_actual)
        print(lista_final)
        context['lista_final'] = lista_final
        context['first_date'] = first_v_date
        context['last_date'] = last_v_date
        context['delta_date'] = delta_date
        # context['paquete'] = paquete
        return context
    
    def post(self, request, *args, **kwargs):
        listado_versiones_url = []
        doc = Documento.objects.get(pk=self.kwargs['pk'])
        versiones = Version.objects.filter(documento_fk=doc)
        for version in versiones:
            static = version.archivo.path
            if static:
                listado_versiones_url.append(static)
        print(listado_versiones_url)
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
        return response

def documentos_con_versiones(request):
    añadidos_list = []
    qs =  Documento.objects.filter(proyecto=request.session.get('proyecto'))
    for doc in qs:
        try:
            version = Version.objects.filter(documento_fk=doc).exists()
            if version:
                añadidos_list.append(doc.pk)
        except Version.DoesNotExist:
            pass
    queryset_final = Documento.objects.filter(pk__in=añadidos_list)
    print(queryset_final)
    return queryset_final
    