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
import datetime

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
    
    def get_versiones_last(self):
        qs1 = self.get_queryset()
        qs2 = Version.objects.select_related('documento_fk').filter(documento_fk__in=qs1) #.select_related("owner").filter(owner__in=users)
        return qs2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = []
        tareas = Tarea.objects.select_related('encargado', 'encargado__perfil', 'documento').filter(documento__proyecto=self.proyecto).order_by('-created_at')
        current_rol = self.request.user.perfil.rol_usuario
        for tarea in tareas:
            rol = tarea.encargado.perfil.rol_usuario

            if current_rol >= 1 and current_rol <= 3:
                if rol >= 1 and rol <= 3:
                    if rol == 1: 
                        pass
                    else:
                        tasks.append(tarea)

            if current_rol >= 4 and current_rol <= 6:
                if rol >= 4 and rol <= 6:
                    if rol == 4: 
                        pass
                    else:
                        tasks.append(tarea)

        context["tareas"] = tasks
        context['Listado'] = self.tabla_status()
        return context

    def tabla_status(self):
        
        #Listar documentos
        lista_inicial = []
        lista_final = []
        semana_actual = timezone.now()
        documentos = self.get_queryset()
        version_documento = 0
        transmital = 0
        dias_revision = 0
        fecha_emision_b = 0
        versiones_documento = self.get_versiones_last()

        for doc in documentos:
            fecha_emision_b = doc.fecha_Emision_B
            comprobacion_first = 0
            version_first = 0
            version = 0
            for versiones in versiones_documento:
                if str(doc.Codigo_documento) == str(versiones.documento_fk) and comprobacion_first == 0:
                    version_first = versiones
                if str(doc.Codigo_documento) == str(versiones.documento_fk):
                    version = versiones

            if version:
                paquete = version.paquete_set.first()
                paquete_first = version_first.paquete_set.first()
                if version.estado_cliente == 5:
                    transmital = abs((paquete.fecha_creacion - paquete_first.fecha_creacion).days)
                    dias_revision = 0
                else:
                    transmital = abs((semana_actual - paquete_first.fecha_creacion).days)
                    fecha_version = paquete.fecha_creacion
                    dias_revision = abs((semana_actual - fecha_version).days)

                version_documento = version.revision

                for revision in TYPES_REVISION[1:4]:
                    if version_documento == revision[0]:
                        if dias_revision < 0:
                            dias_revision = 0
                            lista_inicial =[doc, [version, paquete, semana_actual, '70%', transmital, paquete_first.fecha_creacion, dias_revision]]
                            lista_final.append(lista_inicial)
                        else:
                            lista_inicial =[doc, [version, paquete, semana_actual, '70%', transmital, paquete_first.fecha_creacion, dias_revision]]
                            lista_final.append(lista_inicial)

                for revision in TYPES_REVISION[5:]:
                    if version_documento == revision[0]:
                        lista_inicial = [doc, [version, paquete, semana_actual, '100%', transmital, paquete_first.fecha_creacion, dias_revision]]
                        lista_final.append(lista_inicial)
                        
            else: 
                if semana_actual >= fecha_emision_b:
                    lista_inicial = [doc, ['no version','Atrasado']]
                    lista_final.append(lista_inicial)
                else:
                    lista_inicial = [doc, ['no version','Pendiente']]
                    lista_final.append(lista_inicial)
    
        return lista_final

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
        kwargs["proyecto"] = self.proyecto
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs1 = Tarea.objects.filter(encargado=self.request.user, documento__proyecto=self.proyecto).order_by('-created_at')
        qs2 = Respuesta.objects.filter(tarea__encargado=self.request.user, sent=True, tarea__documento__proyecto=self.proyecto).order_by('-contestado')
        context["tareas"] = qs1
        context["respuestas"] = qs2
        return context

class RespuestaDetail(ProyectoMixin, DetailView):
    template_name = 'status_encargado/respuesta-detail.html'
    context_object_name = 'respuesta'

class TareaDetailView(ProyectoMixin, DetailView):
    model = Tarea
    template_name = 'status_encargado/tarea-detail.html'
    context_object_name = 'tarea'

class TareaEditView(ProyectoMixin, UpdateView):
    model = Tarea
    template_name = 'status_encargado/create-tarea.html'
    form_class = TareaForm
    success_url = reverse_lazy('encargado-index')
    success_message = 'Tarea editada correctamente.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        participantes = self.proyecto.participantes.all()
        kwargs["participantes"] = participantes
        kwargs["usuario"] = user
        return kwargs

class TareaDeleteView(ProyectoMixin, DeleteView):
    model = Tarea
    template_name = 'status_encargado/delete-tarea.html'
    success_message = 'Tarea eliminada correctamente.'
    success_url = reverse_lazy('encargado-index')

class RevisorSentView(ProyectoMixin, ListView):
    template_name = "status_encargado/revisor-enviados.html"
    context_object_name = "respuestas"

    def get_queryset(self):
        qs = Respuesta.objects.filter(tarea__encargado=self.request.user, sent=True).order_by('-contestado')
        return qs

class EncargadoGraficoView(ProyectoMixin, TemplateView):
    template_name = 'status_encargado/graficos.html'

    def get_queryset(self):
        current_rol = self.request.user.perfil.rol_usuario
        if current_rol <= 3 and current_rol >= 1:
            rols = [2,3]
        elif current_rol <= 6 and current_rol >= 4:
            rols = [5,6]

        tareas = Tarea.objects.select_related("encargado").filter(encargado__perfil__rol_usuario__in=rols, documento__proyecto=self.proyecto)         

        return tareas

    def get_queryset_user(self):
        current_rol = self.request.user.perfil.rol_usuario
        if current_rol <= 3 and current_rol >= 1:
            rols = [2,3]
        elif current_rol <= 6 and current_rol >= 4:
            rols = [5,6]
        users = self.proyecto.participantes.all().filter(perfil__rol_usuario__in = rols)

        return users

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        grafico_1 =self.grafico_1()
        grafico_2 =self.grafico_2()
        grafico_3 =self.grafico_3()
        grafico_4 =self.grafico_4()
        grafico_5 =self.grafico_5()
        grafico_6 =self.grafico_6()

        context["grafico_1"] = grafico_1[0]
        context["grafico_1_largo"] = len(grafico_1[0])
        context["tamano_grafico_1"] = grafico_1[1]
        context["espacio_grafico_1"] = grafico_1[2]
        context["grafico_2"] = grafico_2[0]
        context["grafico_2_largo"] = len(grafico_2[0])
        context["tamano_grafico_2"] = grafico_2[1]
        context["espacio_grafico_2"] = grafico_2[2]
        context["grafico_3"] = grafico_3[0]
        context["grafico_3_largo"] = len(grafico_3[0])
        context["tamano_grafico_3"] = grafico_3[1]
        context["espacio_grafico_3"] = grafico_3[2]
        context["grafico_4"] = grafico_4
        context["grafico_4_largo"] = len(grafico_4)
        context["grafico_5"] = grafico_5
        context["grafico_5_largo"] = len(grafico_5)
        context["grafico_6"] = grafico_6[0]
        context["grafico_6_largo"] = len(grafico_6[0])
        context["tamano_grafico_6"] = grafico_6[1]
        context["espacio_grafico_6"] = grafico_6[2]

        return context

    def grafico_1(self):
        """
        Diferencia de tareas y respuetas por cada uno de los participantes.
        """
        final_list = []
        tareas = self.get_queryset()
        users = self.get_queryset_user()
        
        for user in users:
            asignados = 0
            realizados = 0
            for tarea in tareas:
                if tarea.encargado == user:
                    if tarea.estado == True:
                        realizados = realizados + 1
                    asignados = asignados + 1
            if asignados != 0:
                final_list.append([(user.first_name+" "+user.last_name), asignados, realizados])

        lista_grafico_uno = self.tamano_grafico_1(lista_grafico_uno = final_list)
        dividendo = self.espacios_grafico_1(dividendo = lista_grafico_uno)

        final = []
        final.append(final_list)
        final.append(lista_grafico_uno)
        final.append(dividendo)

        return final

    def tamano_grafico_1(self, lista_grafico_uno):

        # lista_grafico_uno = self.grafico_1()
        maximo = 0
        cont = 0

        #Se obtiene el valor máximo del gráfico
        for valores in lista_grafico_uno:
            if cont == 0:
                maximo = valores[1]
                cont = 1
            else:
                if maximo < valores[1]:
                    maximo = valores[1]

        #Se verífica que el maximo sea divisible por 10, para el caso de un maximo superior a 20
        division_exacta = 0
        if maximo > 20:  
            division_exacta = maximo % 10
            while division_exacta != 0:
                maximo = maximo + 1
                division_exacta = maximo % 10
        maximo = maximo + 1

        return maximo

    def espacios_grafico_1(self, dividendo):

        #Llamado para un método definido anteriormente
        # dividendo = self.tamano_grafico_1() - 1
        dividendo = dividendo - 1
        espacios = 0

        #Se secciona el eje en 10 partes iguales
        if dividendo > 20:
            espacios = dividendo / 10
        else:
            espacios = 1

        return int(espacios)
        
    def grafico_2(self):
        """
        Documentos pendientes de cada participante del proyecto.
        """
        final_list = []
        tareas = self.get_queryset()
        users = self.get_queryset_user()
        
        for user in users:
            pendiente = 0
            for tarea in tareas:
                if tarea.encargado == user:
                    if tarea.estado == False:
                        pendiente = pendiente + 1
            if pendiente != 0:
                final_list.append([(user.first_name+" "+user.last_name), pendiente])
        
        lista_grafico_uno = self.tamano_grafico_2(lista_grafico_uno = final_list)
        dividendo = self.espacios_grafico_2(dividendo = lista_grafico_uno)

        final = []
        final.append(final_list)
        final.append(lista_grafico_uno)
        final.append(dividendo)

        return final

    def tamano_grafico_2(self, lista_grafico_uno):

        # lista_grafico_uno = self.grafico_2()
        maximo = 0
        cont = 0

        #Se obtiene el valor máximo del gráfico
        for valores in lista_grafico_uno:
            if cont == 0:
                maximo = valores[1]
                cont = 1
            else:
                if maximo < valores[1]:
                    maximo = valores[1]

        #Se verífica que el maximo sea divisible por 10, para el caso de un maximo superior a 20
        division_exacta = 0
        if maximo > 20:  
            division_exacta = maximo % 10
            while division_exacta != 0:
                maximo = maximo + 1
                division_exacta = maximo % 10
        maximo = maximo + 1

        return maximo

    def espacios_grafico_2(self, dividendo):

        #Llamado para un método definido anteriormente
        # dividendo = self.tamano_grafico_2() - 1
        dividendo = dividendo - 1
        espacios = 0

        #Se secciona el eje en 10 partes iguales
        if dividendo > 20:
            espacios = dividendo / 10
        else:
            espacios = 1

        return int(espacios)

    def grafico_3(self):
        """
        Diferencia entre hh asignadas y hh gastadas por cada uno de los participantes.
        """
        final_list = []
        tareas = self.get_queryset()
        users = self.get_queryset_user()

        for user in users:
            hh_realizados = 0
            hh_asignados = 0
            for tarea in tareas:
                if tarea.encargado == user:
                    hh_asignados = hh_asignados + tarea.contidad_hh
                    try:
                        hh_realizados = hh_realizados + tarea.task_answer.contidad_hh
                    except:
                        pass
            if hh_asignados != 0:
                final_list.append([(user.first_name+" "+user.last_name), hh_asignados, hh_realizados])

        lista_grafico_uno = self.tamano_grafico_2(lista_grafico_uno = final_list)
        dividendo = self.espacios_grafico_2(dividendo = lista_grafico_uno)

        final = []
        final.append(final_list)
        final.append(lista_grafico_uno)
        final.append(dividendo)
        
        return final

    def tamano_grafico_3(self, lista_grafico_uno):

        # lista_grafico_uno = self.grafico_3()
        maximo = 0
        cont = 0

        #Se obtiene el valor máximo del gráfico
        for valores in lista_grafico_uno:
            if cont == 0:
                maximo = valores[1]
                cont = 1
            else:
                if maximo < valores[1]:
                    maximo = valores[1]

        #Se verífica que el maximo sea divisible por 10, para el caso de un maximo superior a 20
        division_exacta = 0
        if maximo > 20:  
            division_exacta = maximo % 10
            while division_exacta != 0:
                maximo = maximo + 1
                division_exacta = maximo % 10
        maximo = maximo + 1

        return maximo

    def espacios_grafico_3(self, dividendo):

        #Llamado para un método definido anteriormente
        # dividendo = self.tamano_grafico_3() - 1
        dividendo = dividendo - 1
        espacios = 0

        #Se secciona el eje en 10 partes iguales
        if dividendo > 20:
            espacios = dividendo / 10
        else:
            espacios = 1

        return int(espacios)

    def grafico_4(self):
        """
        Diferencia entre hh asignadas y hh gastadas total del proyecto.
        """
        final_list = []
        tareas = self.get_queryset()
        total_asignados = 0
        total_realizados = 0

        for tarea in tareas:
            total_asignados = total_asignados + tarea.contidad_hh
            if tarea.estado == True:
                total_realizados = total_realizados + tarea.task_answer.contidad_hh

        final_list.append(total_asignados)
        final_list.append(total_realizados)

        return final_list
                      
    def grafico_5(self):
        """
        Diferencia de tareas y respuetas total del proyecto.
        """

        final_list = []
        tareas = self.get_queryset()
        total_tareas = 0
        total_pendientes = 0

        for tarea in tareas:
            total_tareas = total_tareas + 1
            if tarea.estado == False:
                total_pendientes = total_pendientes + 1 

        final_list.append(total_pendientes)
        final_list.append(total_tareas)

        return final_list

    def grafico_6(self):
        """
        Documentos asignados vs documentos.
        """

        final_list = []
        tareas = self.get_queryset()
        users = self.get_queryset_user()

        for user in users:
            realizados_tiempo = 0
            realizados_atrasados = 0
            atrasados = 0
            asignados = 0
            for tarea in tareas:
                if tarea.encargado == user:
                    asignados = asignados + 1
                    if tarea.estado == True:
                        contador_respuesta =0
                        contador_plazo = 0     
                        tarea_respuesta = ''   
                        tarea_plazo = ''                
                        for respuesta in str(tarea.task_answer.contestado):
                            if contador_respuesta < 10:
                                tarea_respuesta = tarea_respuesta + respuesta
                                contador_respuesta = contador_respuesta + 1
                        for plazo in str(tarea.plazo):
                            if contador_plazo < 10:
                                tarea_plazo = tarea_plazo + plazo
                                contador_plazo = contador_plazo + 1
                        if tarea_respuesta > tarea_plazo:
                            realizados_atrasados = realizados_atrasados + 1
                        else:
                            realizados_tiempo = realizados_tiempo + 1
                    if tarea.estado == False:
                        atrasados = atrasados + 1

            if asignados != 0:
                final_list.append([(user.first_name+" "+user.last_name), realizados_tiempo, realizados_atrasados, atrasados])

        lista_grafico_uno = self.tamano_grafico_2(lista_grafico_uno = final_list)
        dividendo = self.espacios_grafico_2(dividendo = lista_grafico_uno)

        final = []
        final.append(final_list)
        final.append(lista_grafico_uno)
        final.append(dividendo)

        return final

    def tamano_grafico_6(self, lista_grafico_uno):

        # lista_grafico_uno = self.grafico_6()
        maximo = 0
        cont = 0

        #Se obtiene el valor máximo del gráfico
        for valores in lista_grafico_uno:
            if cont == 0:
                maximo_pos_1 = valores[1]
                maximo_pos_2 = valores[2]
                maximo_pos_3 = valores[3]
                cont = 1
            else:
                if maximo_pos_1 < valores[1]:
                    maximo_pos_1 = valores[1]
                if maximo_pos_2 < valores[2]:
                    maximo_pos_2 = valores[2]
                if maximo_pos_3 < valores[3]:
                    maximo_pos_3 = valores[3]
        
        if maximo_pos_1 >= maximo_pos_2 and maximo_pos_1 >= maximo_pos_3:
            maximo = maximo_pos_1
        if maximo_pos_2 >= maximo_pos_1 and maximo_pos_2 >= maximo_pos_3:
            maximo = maximo_pos_2
        if maximo_pos_3 >= maximo_pos_2 and maximo_pos_3 >= maximo_pos_1:
            maximo = maximo_pos_3

        #Se verífica que el maximo sea divisible por 10, para el caso de un maximo superior a 20
        division_exacta = 0
        if maximo > 20:  
            division_exacta = maximo % 10
            while division_exacta != 0:
                maximo = maximo + 1
                division_exacta = maximo % 10
        maximo = maximo + 1

        return maximo

    def espacios_grafico_6(self, dividendo):

        #Llamado para un método definido anteriormente
        # dividendo = self.tamano_grafico_6() - 1
        dividendo = dividendo - 1
        espacios = 0

        #Se secciona el eje en 10 partes iguales
        if dividendo > 20:
            espacios = dividendo / 10
        else:
            espacios = 1

        return int(espacios)
