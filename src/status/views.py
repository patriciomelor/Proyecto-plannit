from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from django.contrib import messages
from django.utils import timezone
from panel_carga.choices import TYPES_REVISION
# from .filters import DocFilter
from panel_carga.models import Documento
from bandeja_es.models import Version, Paquete
# Create your views here.

class StatusIndex(ProyectoMixin, TemplateView):
    template_name = 'status/index.html'

    def get_context_data(self, **kwargs):

        #Listar documentos
        lista_inicial = []
        lista_final = []
        semana_actual = timezone.now()
        version_documento = 0
        transmital = 0

        context = super().get_context_data(**kwargs)
        documentos = Documento.objects.filter(proyecto=self.proyecto)

        for doc in documentos:
            
            version = Version.objects.filter(documento_fk=doc).last()
            
            if version:
                
                paquete = version.paquete_set.all()
                version_documento = version.revision
                transmital = semana_actual.day - version.fecha.day
                
                for revision in TYPES_REVISION[1:4]:

                    if version_documento == revision[0]:
                        
                        lista_inicial = [doc, version, paquete, semana_actual, '70%', transmital]
                        lista_final.append(lista_inicial)

                for revision in TYPES_REVISION[5:]:

                    if version_documento == revision[0]:
                        
                        lista_inicial = [doc, version, paquete, semana_actual, '100%', transmital]
                        lista_final.append(lista_inicial)

                #print('documento: ', doc, ' version: ', version, ' paquete:', paquete, ' listado final: ', lista_final)                

            else: 

                pass
        
        context['Listado'] = lista_final

        return context