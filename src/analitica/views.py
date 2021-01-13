from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from bandeja_es.models import Version
from panel_carga.models import Documento
from panel_carga.choices import ESTADO_CONTRATISTA, ESTADOS_CLIENTE
from datetime import datetime

# Create your views here.


class IndexAnalitica(ProyectoMixin, TemplateView):
    template_name =  'analitica/index.html'
    ###################################################
    #                                                 #
    #                                                 #
    #   PRIMER GRÁFICO DE ESTADOS DE LOS DOCUMENTOS   #
    #                                                 #
    #                                                 #
    ###################################################
    
    def reporte_general(self):

        lista_final = []
        lista_actual = []

        total = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

        lista_final.append(lista_actual)

        for doc in documentos:
            versiones = Version.objects.filter(documento_fk=doc).last()
            lista_actual = [versiones, doc] 
            lista_final.append(lista_actual)

        estados_documento = []
        estados_final = []

        #total = 0

        for estado in ESTADOS_CLIENTE[1:]:
            cont = 0

            for lista in lista_final:

                try:
                    estado_documento = lista[0].estado_cliente
                    
                    if estado_documento == estado[0] :
                        cont = cont + 1
                    
                    estados_documentos = [cont, estado[1]]
                    estados_final.append(estados_documentos)
                
                except IndexError:
                    pass

                except AttributeError:
                    pass

            #total = total + cont
        
        # if cont == 0:
        #     total = 0
        #     estados_documentos = [total, 'Documentos Totaless']

        # if cont != 0:
        #     estados_documentos = [total, 'Documentos Totaless']
        estados_documentos = [total, 'Documentos Totaless']
        estados_final.append(estados_documentos)

        # for estado in ESTADOS_CLIENTE[1:]:

        #     version_aprobadocCs = Version.objects.filter(estado_cliente=int(estado[0]), documento_fk__in=doc).count()
        #     lista_actual = [version_aprobadocCs, estado[1]]
        #     lista_final.append(lista_actual)
        #     total = total + version_aprobadocCs

        return estados_final

    ###################################################
    #                                                 #
    #                                                 #
    #   SEGUNDO GRÁFICO DE EMITIDOS POR SUBESTACION   #
    #                                                 #
    #                                                 #
    ###################################################

    def reporte_emisiones(self):
        
        lista_actual = []
        lista_final = []

        especialidad_list = tuple()
        cantidad_por_especialidad = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

        #versiones actuales de los documentos
        for doc in documentos:
            versiones = Version.objects.filter(documento_fk=doc).last()
            lista_actual = [versiones, doc] 
            lista_final.append(lista_actual) 

        for lista in lista_final: 
            for special in documentos:
                especialidad_actual = special.Especialidad
                if not especialidad_actual in especialidad_list:
                    especialidad_list = especialidad_list + (str(especialidad_actual),)

        #lista final de versiones aprobadas
        aprobados_final = []
        aprobados_inicial = []
        
        for especialidad in especialidad_list:
            cont = 0 
            
            for lista in lista_final: 

                try:
                    mi_especialidad = lista[1].Especialidad
                    mi_estado_cliente = lista[0].estado_cliente

                    if mi_especialidad == especialidad and ( mi_estado_cliente == 1 or mi_estado_cliente == 4 or mi_estado_cliente == 5 ) :
                        cont = cont + 1

                except AttributeError:
                    pass

            aprobados_inicial = [cont, especialidad]
            aprobados_final.append(aprobados_inicial) 

        return aprobados_final      

        ###################################################
        #                                                 #
        #                                                 #
        #   TERCER GRÁFICO DE STATUS POR ESPECIALIDAD     #
        #                                                 #
        #                                                 #
        ###################################################

    def reporte_aprobadosConstruccion_documentos(self):
        lista_actual = []
        lista_final = []

        especialidad_list = tuple()
        cantidad_por_especialidad = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

        for doc in documentos:
            versiones = Version.objects.filter(documento_fk=doc).last()
            lista_actual = [versiones, doc] 
            lista_final.append(lista_actual)

        for special in documentos:
                especialidad_actual = special.Especialidad
                if not especialidad_actual in especialidad_list:
                    especialidad_list = especialidad_list + (str(especialidad_actual),)

        aprobados_final = []
        aprobados_inicial = []
        
        for especialidad in especialidad_list:
            cont = 0 
            
            for lista in lista_final: 

                try:
                    mi_especialidad = lista[1].Especialidad
                    mi_estado_cliente = lista[0].estado_cliente

                    if mi_especialidad == especialidad and mi_estado_cliente == 5 :
                        cont = cont + 1

                except AttributeError:
                    pass

            aprobados_inicial = [cont, especialidad]
            aprobados_final.append(aprobados_inicial)

        
        # for lista in especialidad_list:
        #         cont2 = 0
        #         for doc in documentos:
        #             if lista == doc.Especialidad:
        #                 cont2 = cont2 + 1
        #         lista_actual = [cont2, lista]
        #         lista_final.append(lista_actual)

        return aprobados_final

    def reporte_total_documentos(self):
        
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        especialidad_list = tuple()

        for special in documentos:
            especialidad_actual = special.Especialidad
            if not especialidad_actual in especialidad_list:
                especialidad_list = especialidad_list + (str(especialidad_actual),)

        aprobados_final = []
        aprobados_inicial = []

        for especialidad in especialidad_list:
            cont = 0
            
            for doc in documentos: 
                
                try:

                    mi_especialidad = doc.Especialidad

                    if mi_especialidad == especialidad:
                        cont = cont + 1

                except AttributeError:
                    pass

            aprobados_inicial = [cont, especialidad]
            aprobados_final.append(aprobados_inicial)   

        return aprobados_final

        ###################################################
        #                                                 #
        #                                                 #
        #   CUARTO GRÁFICO DE CURVA S                     #
        #                                                 #
        #                                                 #
        ###################################################


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lista_final'] = self.reporte_general()
        context['lista_emisiones'] = self.reporte_emisiones()
        context['lista_aprobadosConstruccion_documentos'] = self.reporte_aprobadosConstruccion_documentos()
        context['lista_total_documentos'] = self.reporte_total_documentos()

        return context