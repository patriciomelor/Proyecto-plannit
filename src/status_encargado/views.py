from django.db.models.query_utils import select_related_descend
from django.forms.forms import Form
from django.shortcuts import redirect, render
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

from .models import Tarea, Respuesta
from status_encargado import models
# Create your views here.
class EncargadoIndex(ProyectoMixin, TemplateView):
    template_name = 'status_encargado/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.perfil.rol_usuario == 1 or request.user.perfil.rol_usuario == 4:
            return super(EncargadoIndex, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('revisor-index')

    def get_queryset(self):
        queryset=Documento.objects.filter(proyecto=self.proyecto)
        return queryset
    

    def tabla_status(self):
        #Listar documentos
        lista_inicial = []
        lista_final = []
        semana_actual = timezone.now()
        version_documento = 0
        transmital = 0
        dias_revision = 0
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

        return lista_final



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = Tarea.objects.all()
        print(tasks)
        context["tareas"] = tasks
        context['Listado'] = self.tabla_status()
        return context

class TablaEncargado(ProyectoMixin, FormView):
    template_name = 'status_encargado/list-encargado.html'

class CreateTarea(ProyectoMixin, CreateView):
    model = Tarea
    template_name = 'status_encargado/create-tarea.html'
    form_class = TareaForm
    success_url = reverse_lazy('encargado-index')
    success_message = 'Tarea asignada correctamente.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        participantes = self.proyecto.participantes.all()
        kwargs["participantes"] = participantes
        kwargs["usuario"] = user
        return kwargs

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
        doc_pk = Documento.objects.get(pk=self.kwargs["doc_pk"])
        initial["documento"] = doc_pk
        return initial

class CreateRespuesta(ProyectoMixin, CreateView):
    template_name = 'status_encargado/create-respuesta.html'
    form_class = RespuestaForm
    success_url = reverse_lazy('revisor-index')
    success_message = 'Respuesta enviada correctamente.'

    def form_valid(self, form):
        answer = form.save(commit=False)
        task = Tarea.objects.get(pk=self.kwargs["task_pk"])
        task.estado = True
        task.save()
        answer.tarea = task
        answer.sent = True
        answer.save()
        return super().form_valid(form)

class RevisorView(ProyectoMixin, ListView):
    template_name = "status_encargado/revisor-index.html"
    context_object_name = "tareas"

    def get_queryset(self):
        qs = Tarea.objects.filter(encargado=self.request.user).order_by('-created_at')
        return qs

class RevisorSentView(ProyectoMixin, ListView):
    template_name = "status_encargado/revisor-enviados.html"
    context_object_name = "respuestas"

    def get_queryset(self):
        qs = Respuesta.objects.filter(tarea__encargado=self.request.user, sent=True).order_by('-contestado')
        return qs

class EncargadoGraficoView(ProyectoMixin, TemplateView):
    template_name = 'status_encargado/graficos.html'

    def grafico_1(self):
        """
        diferencia de tareas y respuetas porcada uno de los participantes 
        """
        final_list = []
        participantes = self.proyecto.participantes.all()
        for user in participantes:
            realizados = 0
            asignados = 0
            tareas = Tarea.objects.filter(encargado=user)
            for tarea in tareas:
                asignados = asignados + 1
                if tarea.estado == True:
                    realizados = realizados + 1

            final_list.append([(user.first_name+" "+user.last_name), asignados, realizados])

        return final_list
        
    def grafico_2(self):
        """
        Documentos pendientes de cada participante
        """
        final_list = []
        participantes = self.proyecto.participantes.all()
        for user in participantes:
            asignados = 0
            tareas = Tarea.objects.filter(encargado=user)
            for tarea in tareas:
                if tarea.estado == False:
                    asignados = asignados + 1

            final_list.append([(user.first_name+" "+user.last_name), asignados])

        return final_list

    def grafico_3(self):
        """
        diferencia entre hh asignadas y hh gastadas porcada uno de los participantes 
        """
        final_list = []
        participantes = self.proyecto.participantes.all()
        for user in participantes:
            hh_realizados = 0
            hh_asignados = 0
            tareas = Tarea.objects.filter(encargado=user)
            for tarea in tareas:
                hh_asignados = hh_asignados + tarea.contidad_hh
                try:
                    hh_realizados = hh_realizados + tarea.task_answer.contidad_hh
                except:
                    pass
            final_list.append([(user.first_name+" "+user.last_name), hh_asignados, hh_realizados])
        
        return final_list

    def grafico_4(self):
        """
        diferencia entre hh asignadas y hh gastadas total del proyecto
        """
        final_list = []
        tasks = Tarea.objects.filter(documento__proyecto=self.proyecto)
        total_asignados = 0
        total_realizados = 0
        for task in tasks:
            if task.estado == False:
                total_asignados = total_asignados + task.contidad_hh
            else:
                total_realizados = total_realizados + task.task_answer.contidad_hh
        final_list.append(total_asignados)
        final_list.append(total_realizados)
        return final_list
                
        
    def grafico_5(self):
        """
        diferencia de tareas y respuetas total del proyecto
        """
        final_list = []
        tasks = Tarea.objects.filter(documento__proyecto=self.proyecto)
        total_tareas = 0
        total_respuestas = 0
        for task in tasks:
            total_tareas = total_tareas + 1
            if task.estado == True:
                total_respuestas = total_respuestas + 1 
        final_list.append(total_tareas)
        final_list.append(total_respuestas)
        return final_list

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        g1 =self.grafico_1()
        g2 =self.grafico_2()
        g3 =self.grafico_3()
        g4 =self.grafico_4()
        g5 =self.grafico_5()
        print("Grafico N°1: -->",g1)
        print("Grafico N°2: -->",g2)
        print("Grafico N°3: -->",g3)
        print("Grafico N°4: -->",g4)
        print("Grafico N°5: -->",g5)
        context["grafico_1"] = g1
        context["grafico_2"] = g2
        context["grafico_3"] = g3
        context["grafico_4"] = g4
        context["grafico_5"] = g5
        return context