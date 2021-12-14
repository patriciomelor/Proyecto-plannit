import time
from django.db.models.query import ValuesIterable
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from django.contrib import messages
import requests
import os.path
import zipfile
from io import BytesIO
from django.conf import settings

from .filters import DocFilter
from panel_carga.models import Documento
from bandeja_es.models import Version, Paquete

# Create your views here.

class BuscadorIndex(ProyectoMixin, View):
    template_name = 'buscador/index.html'
    model = Documento
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        añadidos_list = []
        qs =  Documento.objects.prefetch_related('version_set').filter(proyecto=self.proyecto)
        for doc in qs:
            if doc.version_set.exists():
                last_version = doc.version_set.last()
                try:
                    añadidos_list.append([doc, last_version.pk, last_version.get_revision_display(), last_version.archivo.url ])
                except ValueError:
                    pass
        
        context["documentos"] = añadidos_list
        return context

    def get (self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        listado = self.request.POST.getlist('dnld')
        versiones = Version.objects.filter(pk__in=listado)
        zip_subdir = "Ultimas-Versiones-{0}-{1}".format(self.proyecto.nombre, time.strftime('%d-%m-%y'))
        zip_filename = "%s.zip" % zip_subdir
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w")
        for version in versiones:
            try:
                r = requests.get(version.archivo.url, stream=True)
            # print("VERSION: ", version)
            # print("STATUS: ",r.status_code)
            # print("CONTENIDO: ",r.content)
            # print("TEXTO: ",r.text)
            # print("JOSN: ",r.json)
                zf.writestr(str(version.archivo), r.content)
            except ValueError:
                error = "Error en la version {}, no tiene archivo asociado".format(version)
        zf.close()
        response = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

        return response
class VersionesList(ProyectoMixin, DetailView):
    model = Documento
    template_name = 'buscador/detalle.html'
    context_object_name = 'documento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        versiones = Version.objects.select_related("documento_fk").prefetch_related("paquete_set", "paquete_set__owner").filter(documento_fk__pk=self.kwargs['pk']).order_by("fecha")
        try:
            first_v_date = versiones[0]
            last_v_date = versiones.reverse()[0]
            paquete_first = first_v_date.paquete_set.first()
            paquete_last = last_v_date.paquete_set.first()
            delta_date = abs((last_v_date.fecha - first_v_date.fecha).days)
        
        except:
            pass

        context['versiones'] = versiones
        context['first_date'] = paquete_first.fecha_creacion
        context['last_date'] = paquete_last.fecha_creacion
        context['delta_date'] = delta_date
        # context['paquete'] = paquete
        return context
    
    def post(self, request, *args, **kwargs):
        listado_versiones_url = []
        doc = Documento.objects.get(pk=self.kwargs['pk'])
        versiones = Version.objects.filter(documento_fk=doc)
        for version in versiones:
            try:
                static = version.archivo.url
                if static:
                    listado_versiones_url.append(version)
            except ValueError:
                pass
        zip_subdir = "Documento-{0}-{1}".format(doc.Codigo_documento, time.strftime('%d-%m-%y'))
        zip_filename = "%s.zip" % zip_subdir
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w")
        for version in listado_versiones_url:
            r = requests.get(version.archivo.url, stream=True)
            zf.writestr(str(version.archivo), r.content)
        zf.close()
        response = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return response
