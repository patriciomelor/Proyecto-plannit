from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import FormView
from panel_carga.views import ProyectoMixin
from django.contrib.auth.models import User
from .filters import DocFilter
from panel_carga.models import Documento
from bandeja_es.models import Version, Paquete
from django.utils import timezone
from panel_carga.choices import TYPES_REVISION, ESTADOS_CLIENTE


# Create your views here.

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

class RootView(RedirectView):
    pattern_name = 'account_login'

class IndexView(ProyectoMixin, TemplateView):
    template_name = "index-base.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proyecto"] = self.proyecto
        return context
    

class EscritorioView(ProyectoMixin, TemplateView):
    template_name = "administrador/Escritorio/dash.html"

    def get_queryset(self):
        listado_versiones_doc = DocFilter(self.request.GET, queryset=Documento.objects.filter(proyecto=self.proyecto))
        return listado_versiones_doc.qs.order_by('Codigo_documento')

    def get_context_data(self, **kwargs):
        #Listar documentos
        lista_inicial = []
        lista_final = []
        lista_inicial_emitidos = []
        lista_final_emitidos = []
        #################################################################   

        #Variables
        semana_actual = timezone.now()
        cantidad_documentos = 0
        cantidad_versiones = 0
        contador_atrasados = 0
        especialidad_list = tuple()

        context = super().get_context_data(**kwargs)
        documentos = self.get_queryset()
        #################################################################

        #Obtener especialidades de los documentos
        for special in documentos:
            especialidad_actual = special.Especialidad
            if not especialidad_actual in especialidad_list:
                especialidad_list = especialidad_list + (str(especialidad_actual),)
        #################################################################  

        #Obtener listas de documentos emitidos y no emitidos
        for doc in documentos:
            version = Version.objects.filter(documento_fk=doc).last()
            if version:
                lista_inicial_emitidos = [doc, version]
                lista_final_emitidos.append(lista_inicial_emitidos) 
                
            if not version:                
                lista_inicial = [doc, []]
                lista_final.append(lista_inicial)        
        #################################################################    

        #Obtener documentos sin emisiones por especialidad
        lista_atrasados_final = []
        
        for especialidad in especialidad_list:
            lista_atrasados = []
            contador = 0
            for doc in lista_final:
                if especialidad == doc[0].Especialidad:
                    lista_atrasados.append(doc[0])
                    contador = contador + 1
            if contador != 0:
                lista_atrasados_final.append(lista_atrasados)
        #################################################################   

        #Obtener documentos con emisiones porespecialidad
        lista_emitidos_final = []
        avance_real = 0
        
        for especialidad in especialidad_list:
            lista_emitidos = []
            contador = 0
            for doc in lista_final_emitidos:
                if especialidad == doc[0].Especialidad:
                    lista_emitidos.append(doc[0])
                    contador = contador + 1
            if contador != 0:
                lista_emitidos_final.append(lista_emitidos)

        #Obtener documentos emitidos vs documentos atrasados
        lista_datos_final = []
        porcentaje = 0

        for especialidad in especialidad_list:
            lista_datos_inicial = []
            contador_total = 0
            contador_no_emitidos = 0
            for doc in documentos:
                version = Version.objects.filter(documento_fk=doc).last()
                if version:
                    if especialidad == doc.Especialidad:
                        contador_total = contador_total + 1
                if not version:
                    if especialidad == doc.Especialidad:
                        contador_no_emitidos = contador_no_emitidos + 1
            
            #Calculo de datos superiores
            cantidad_versiones = cantidad_versiones + contador_total
            contador_total = contador_total + contador_no_emitidos
            cantidad_documentos = cantidad_documentos + contador_total
            contador_atrasados = contador_atrasados + contador_no_emitidos
            porcentaje_documentos_emitidos = (cantidad_versiones * 100)/cantidad_documentos               
            porcentaje = (contador_no_emitidos/contador_total)*100
            porcentaje = format(porcentaje, '.1f')
            print(porcentaje)
            lista_datos_inicial = [especialidad, contador_total, contador_no_emitidos, porcentaje]
            lista_datos_final.append(lista_datos_inicial)
        ########################################################################################

        context['Porcentaje'] = format(porcentaje_documentos_emitidos, '.2f')
        context['Cantidad'] = cantidad_documentos
        context['Emitidos'] = cantidad_versiones
        context['Atrasados'] = contador_atrasados
        context['Listado_no_emitidos'] = lista_atrasados_final
        context['Comparacion'] = lista_datos_final
        context['Listado_emitidos'] = lista_emitidos_final
        context['Listado_final'] = lista_final_emitidos

        return context

