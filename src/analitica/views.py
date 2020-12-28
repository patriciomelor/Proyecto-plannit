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
        try: 
            for v in versiones_pk_list:
                if (version.estado_cliente == 1):
                    AprobadocC = AprobadocC + 1
                elif (version.estado_cliente == 2):
                    Rechazado = Rechazado + 1
                elif (version.estado_cliente == 3):
                    Eliminado = Eliminado + 1
                elif (version.estado_cliente == 4):
                    Aprobado = Aprobado + 1
                elif (version.estado_cliente == 5):
                    ValidoCons = ValidoCons + 1
                elif (version.estado_cliente == 6):
                    AprobadoNum = AprobadoNum + 1
            data.append(AprobadocC)
            data.append(Rechazado)
            data.append(Eliminado)
            data.append(Aprobado)
            data.append(ValidoCons)
            data.append(AprobadoNum)
            #data = [AprobadocC, Rechazado, Eliminado, Aprobado, ValidoCons, AprobadoNum]
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_states'] = self.get_report_states()
        return context