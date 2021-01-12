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

        doc = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        total = len(doc)

        lista_actual = [total, 'Total de Documentos']
        lista_final.append(lista_actual)

        for estado in ESTADOS_CLIENTE[1:]:

            version_aprobadocCs = Version.objects.filter(estado_cliente=int(estado[0]), documento_fk__in=doc).count()
            lista_actual = [version_aprobadocCs, estado[1]]
            print(lista_actual)
            lista_final.append(lista_actual)
            total = total + version_aprobadocCs

        #print(lista_final)

        return lista_final

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
        versiones = Version.objects.filter(documento_fk__in=documentos, estado_cliente=5)

        id_ver = []
        fecha_list = []
        # aprc_cont = 0
        # rec_cont = 0
        # eli_cont = 0
        # apr_cont = 0
        # apr_cont = 0
        # apr_cont = 0

        for doc in documentos:
            especialidad_actual = doc.Especialidad
            if not especialidad_actual in especialidad_list:
                especialidad_list = especialidad_list + (str(especialidad_actual),)
            for estado in ESTADOS_CLIENTE[1:]:
                versiones = Version.objects.filter(estado_cliente=int(estado[0]), documento_fk=doc).last()
                lista_actual = [versiones, estado[1], especialidad_actual] 
                lista_final.append(lista_actual) # lista final = [ [versiones, estado[1], especialidad_actual] , [versiones, estado[1], especialidad_actual] , ... , [versiones, estado[1], especialidad_actual] ]
        
        # for lista in lista_final: # lista = [versiones, estado[1], especialidad_actual] --> lasta[2] = especialidad_actual
        #     for special in documentos:
        #         especialidad_actual = special.Especialidad
        #         if not especialidad_actual in especialidad_list:
        #             especialidad_list = especialidad_list + (str(especialidad_actual),)
        #     if lista[2] ==

            # versiones = Version.objects.filter(documento_fk=doc).last()
            # especialidad_actual = doc.Especialidad
            # if versiones.estado_cliente == 1:
            #     aprc_cont = apr_cont + 1
            # else:
            #     if versiones.estado_cliente == 2:
            #     rec_cont = rec_cont + 1
            #     else:
            #         if versiones.estado_cliente == 3:
            #             eli_cont = eli_cont + 1
            #         else:
            #             if versiones.estado_cliente == 4:
            #                 apr_cont = apr_cont + 1
            #             else:
            #                 if versiones.estado_cliente == 5:
            #                     apr_cont = apr_cont + 1

            # # if versiones.fecha > versiones.fechasiguiente: esto hay que hacer conceptualmente 
            # #     version definitiva 

            # fecha_list = [versiones.fecha] # fecha_list = [[10/03/2020, 18/12/2019,....., 18/12/2019],[...],....,[...]]
            # #id_ver = [versiones.id] fecha_list = [[3, 5,....., 546],[...],....,[...]]
            # for actu in fecha_list[0]:
            #     if len(fecha_ultima_ver) == 0:
            #         fecha_ultima_ver = actu # fecha de version   10/03/2020
            #         #id_ultimo = versiones.id # id de version  3
            #     else:
            #         if actu == fecha_ultima_ver
            #             #aqui encontramos la fecha 12/12/12






        # for lista in especialidad_list:
        #     cont2 = 0
        #     for doc in documentos:
        #         if lista == doc.Especialidad:
        #             cont2 = cont2 + 1
        #     lista_actual = [cont2, lista]
        #     lista_final.append(lista_actual)     

        # for especial in especialidad_list:
        #     doc = Documento.objects.filter(proyecto=self.request.session.get('proyecto'), Especialidad=especial)
        #     versiones = Versio.objects.filter(documento_fk__in=doc).count()
        #     print(versiones)
        #for especialidad, numero in zip(especialidad_list, cantidad_por_especialidad):            recorrer dos listas en el mismo tiempo
        #    diccionario.update({str(especialidad) : numero})  

        print(versiones)

        return lista_final      

        ###################################################
        #                                                 #
        #                                                 #
        #   TERCER GRÁFICO DE STATUS POR ESPECIALIDAD     #
        #                                                 #
        #                                                 #
        ###################################################

    def reporte_total_documentos(self):
        lista_actual = []
        lista_final = []

        especialidad_list = tuple()
        cantidad_por_especialidad = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

        for special in documentos:
                especialidad_actual = special.Especialidad
                if not especialidad_actual in especialidad_list:
                    especialidad_list = especialidad_list + (str(especialidad_actual),)

        for lista in especialidad_list:
                cont2 = 0
                for doc in documentos:
                    if lista == doc.Especialidad:
                        cont2 = cont2 + 1
                lista_actual = [cont2, lista]
                lista_final.append(lista_actual)

        return lista_final

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lista_final'] = self.reporte_general()
        context['lista_emisiones'] = self.reporte_emisiones()
        context['lista_total_documentos'] = self.reporte_total_documentos()

        return context