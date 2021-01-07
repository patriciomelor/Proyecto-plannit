from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from bandeja_es.models import Version
from panel_carga.models import Documento
from panel_carga.choices import ESTADO_CONTRATISTA, ESTADOS_CLIENTE

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

        print(lista_final)

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
        especialidad_final = []
        cantidad_por_especialidad = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

        for special in documentos:
            especialidad_actual = special.Especialidad
            if not especialidad_actual in especialidad_list:
                especialidad_list = especialidad_list + (str(especialidad_actual),)
                especialidad_final.append(especialidad_list)

        for lista in especialidad_final:
            cont2 = 0
            for doc in documentos:
                if lista == doc.Especialidad:
                    cont2 = cont2 + 1
                    
            cantidad_por_especialidad.append(cont2)
            
            lista_actual.append(cantidad_por_especialidad, lista)
            lista_final.append(lista_actual) 

        # for especial in especialidad_list:
        #     doc = Documento.objects.filter(proyecto=self.request.session.get('proyecto'), Especialidad=especial)
        #     versiones = Versio.objects.filter(documento_fk__in=doc).count()
        #     print(versiones)
        #for especialidad, numero in zip(especialidad_list, cantidad_por_especialidad):            recorrer dos listas en el mismo tiempo
        #    diccionario.update({str(especialidad) : numero})  

        return lista_final      

    def reporte_especialidadades(self):
        especialidad_list = tuple()
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

        for special in documentos:
            especialidad_actual = special.Especialidad
            if not especialidad_actual in especialidad_list:
                especialidad_list = especialidad_list + (str(especialidad_actual),)

        return especialidad_list

        ###################################################
        #                                                 #
        #                                                 #
        #   TERCER GRÁFICO DE STATUS POR ESPECIALIDAD     #
        #                                                 #
        #                                                 #
        ###################################################

        def reporte_aprobados(self):
            lista_final2 = []
            lista_inicial2 = []

            doc = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

            for estado in ESTADOS_CLIENTE[1:]:

                version_especialidad_aprobado = Version.objects.filter(estado_cliente = int(0), documento_fk__int=doc).count()
                lista_actual = [version_especialidad_aprobado, ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista_emisiones'] = self.reporte_emisiones()
        context['lista_especialidades'] = self.reporte_especialidadades()
        context['lista_final'] = self.reporte_general()

        return context