from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from bandeja_es.models import Version

# Create your views here.


class IndexAnalitica(ProyectoMixin, TemplateView):
    template_name =  'analitica/index.html'
 
    def get_report_states(self):
        data = []
        version_aprobadocCs = Version.objects.filter(estado_cliente = 1).count() #Aprobado con comentarios
        version_rechazados = Version.objects.filter(estado_cliente = 2).count() #Rechazado
        version_eliminados = Version.objects.filter(estado_cliente = 3).count() #Eliminado
        version_aprobados = Version.objects.filter(estado_cliente = 4).count() #Aprobado
        version_validoConss = Version.objects.filter(estado_cliente = 5).count() #Valido para construcción
        version_aprobadoNums = Version.objects.filter(estado_cliente = 6).count() #Aproba en numeros
        data = [version_aprobadocCs,version_rechazados,version_eliminados,version_aprobados,version_validoConss,version_aprobadoNums]
        # data.append(version_aprobadocCs)
        # data.append(version_rechazados)
        # data.append(version_eliminados)
        # data.append(version_aprobados)
        # data.append(version_validoConss)
        # data.append(version_aprobadoNums)
        #data = [AprobadocC, Rechazado, Eliminado, Aprobado, ValidoCons, AprobadoNum]
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_states'] = self.get_report_states()
        return context