from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from django.contrib import messages
from django.utils import timezone
from panel_carga.choices import TYPES_REVISION, ESTADOS_CLIENTE
# from .filters import DocFilter
from panel_carga.models import Documento
from bandeja_es.models import Version, Paquete
from .filters import DocFilter

# Create your views here.

class StatusIndex(ProyectoMixin, TemplateView):
    template_name = 'status/index.html'
    
    def get_queryset(self):
        listado_versiones_doc = DocFilter(self.request.GET, queryset=Documento.objects.filter(proyecto=self.proyecto))
        return listado_versiones_doc.qs.order_by('Codigo_documento')
    
    def get_context_data(self, **kwargs):
        #Listar documentos
        lista_inicial = []
        lista_final = []
        semana_actual = timezone.now()
        version_documento = 0
        transmital = 0
        dias_revision = 0
        fecha_emision_b = 0
        context = super().get_context_data(**kwargs)
        documentos = self.get_queryset()
        for doc in documentos:
            fecha_emision_b = doc.fecha_Emision_B
            version = Version.objects.filter(documento_fk=doc).last()
            version_first = Version.objects.filter(documento_fk=doc).first()
            if version:
                paquete = version.paquete_set.all()
                paquete_first = version_first.paquete_set.all()
                estado_version = version.revision
                if version.estado_cliente == 5:
                    transmital = abs((paquete[0].fecha_creacion - paquete_first[0].fecha_creacion).days)
                else:
                    transmital = abs((semana_actual - paquete_first[0].fecha_creacion).days)
                version_documento = version.revision
                if estado_version == 1 or estado_version == 2 or estado_version == 3 or estado_version == 4:
                    fecha_version = version_first.fecha
                    dias_revision = abs((semana_actual - fecha_version).days)
                if estado_version >= 5 and version.estado_cliente == 5:
                    fecha_version_actual = version.fecha
                    fecha_version_primera = version_first.fecha
                    dias_revision = abs((fecha_version_actual - fecha_version_primera).days)
                if estado_version >= 5 and version.estado_cliente != 5:
                    fecha_version_primera = version_first.fecha
                    dias_revision = abs((semana_actual - fecha_version_primera).days)

                for revision in TYPES_REVISION[1:4]:
                    if version_documento == revision[0]:
                        if dias_revision < 0:
                            dias_revision = 0
                            lista_inicial =[doc, [version, paquete, semana_actual, '70%', transmital, paquete_first[0].fecha_creacion, dias_revision]]
                            lista_final.append(lista_inicial)
                        else:
                            lista_inicial =[doc, [version, paquete, semana_actual, '70%', transmital, paquete_first[0].fecha_creacion, dias_revision]]
                            lista_final.append(lista_inicial)

                for revision in TYPES_REVISION[5:]:
                    if version_documento == revision[0]:
                        lista_inicial = [doc, [version, paquete, semana_actual, '100%', transmital, paquete_first[0].fecha_creacion, dias_revision]]
                        lista_final.append(lista_inicial)

            else: 
                if semana_actual >= fecha_emision_b:
                    lista_inicial = [doc, ['no version','Atrasado']]
                    lista_final.append(lista_inicial)
                else:
                    lista_inicial = [doc, ['no version','Pendiente']]
                    lista_final.append(lista_inicial)
                
        context['Listado'] = lista_final
        context['filter'] = DocFilter(self.request.GET, queryset=documentos)
        return context