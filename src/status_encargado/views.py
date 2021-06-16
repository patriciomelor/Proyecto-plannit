from django.forms.forms import Form
from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from bandeja_es.models import Version, Paquete
from panel_carga.models import Documento
from django.utils import timezone
from django.contrib import messages
from panel_carga.choices import TYPES_REVISION, ESTADOS_CLIENTE
from status_encargado.forms import RespuestaForm, TareaForm
# Create your views here.
class EncargadoIndex(ProyectoMixin, TemplateView):
    template_name = 'status_encargado/index.html'

    def get_queryset(self):
        queryset=Documento.objects.filter(proyecto=self.proyecto)
        return queryset
    
    def get_context_data(self, **kwargs):
        #Listar documentos
        lista_inicial = []
        lista_final = []
        semana_actual = timezone.now()
        version_documento = 0
        transmital = 0
        dias_revision = 0
        context = super().get_context_data(**kwargs)
        documentos = self.get_queryset()
        for doc in documentos:
            version = Version.objects.filter(documento_fk=doc).last()
            version_first = Version.objects.filter(documento_fk=doc).first()
            if version:
                paquete = version.paquete_set.all()
                paquete_first = version_first.paquete_set.all()
                if version.estado_cliente == 5:
                    transmital = paquete[0].fecha_creacion - paquete_first[0].fecha_creacion
                    dias_revision = 0
                else:
                    transmital = semana_actual - paquete_first[0].fecha_creacion
                    dias_revision = semana_actual.day - version.fecha.day
                
                version_documento = version.revision
                for revision in TYPES_REVISION[1:4]:
                    if version_documento == revision[0]:
                        if dias_revision < 0:
                            dias_revision = 0
                            lista_inicial =[doc, [version, paquete, semana_actual, '70%', transmital.days, paquete_first[0].fecha_creacion, dias_revision]]
                            lista_final.append(lista_inicial)
                        else:
                            #dias_revision = 0
                            lista_inicial =[doc, [version, paquete, semana_actual, '70%', transmital.days, paquete_first[0].fecha_creacion, dias_revision]]
                            lista_final.append(lista_inicial)

                for revision in TYPES_REVISION[5:]:
                    if version_documento == revision[0]:
                        lista_inicial = [doc, [version, paquete, semana_actual, '100%', transmital.days, paquete_first[0].fecha_creacion, dias_revision]]
                        lista_final.append(lista_inicial)
                #print('documento: ', doc, ' version: ', version, ' paquete:', paquete, ' listado final: ', lista_final) 



            else: 
                lista_inicial = [doc, []]
                lista_final.append(lista_inicial)
                
        context['Listado'] = lista_final
        return context

class TablaEncargado(ProyectoMixin, ListView):
    template_name = 'status_encargado/list-encargado.html'
class CreateTarea(ProyectoMixin, FormView):
    template_name = 'status_encargado/create-tarea.html'
    form_class = TareaForm

    def form_valid(self, form, **kwargs):
        tarea = form.save(commit=False)
        
class CreateRespuesta(ProyectoMixin, FormView):
    template_name = 'status_encargado/create-respuesta.html'
    form_class = RespuestaForm