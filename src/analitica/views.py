from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from bandeja_es.models import Version
from panel_carga.models import Documento
from panel_carga.choices import ESTADO_CONTRATISTA, ESTADOS_CLIENTE, TYPES_REVISION
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

        #lista_final.append(lista_actual)

        for doc in documentos:
            versiones = Version.objects.filter(documento_fk=doc).last()
            lista_actual = [versiones, doc] 
            lista_final.append(lista_actual)

        estados_documento = []
        estados_final = []

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

        estados_documentos = [total, 'Documentos Totaless']
        estados_final.append(estados_documentos)

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
        cantidad_por_especialidad = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        documentos_contador = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        #versiones actuales de los documentos
        lista_final = []

        especialidad_list = tuple()
        for doc in documentos:
            cont = 0
            versiones = Version.objects.filter(documento_fk=doc).last()

            for revision in ESTADOS_CLIENTE[1:]:
                
                try:

                    if revision[0] == versiones.revision:
                        cont = 1

                except AttributeError:

                    pass

            if cont == 0:

                lista_actual = [versiones, doc] 
                print(lista_actual)
                print('Primera lista')
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
                    #mi_estado_cliente = lista[0].estado_cliente

                    if mi_especialidad == especialidad:
                        cont = cont + 1

                except AttributeError:
                    pass

            aprobados_inicial = [cont, especialidad]

            print(aprobados_inicial)
            print('Segunda lista')

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

    def reporte_curva_s_fechas(self):
        
        lista_actual = []
        lista_final = []

        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        valor_ganado = (valor_ganado / 100)
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

        for doc in documentos:

            fecha_emision_b = doc.fecha_Emision_B
            fecha_emision_0 = doc.fecha_Emision_0

            lista_acual = [fecha_emision_b, fecha_emision_0]
            lista_final.append(lista_acual)
        
        # fecha_final_b = 
        # fecha_final_0 = 

        cont = 1

        for lista in documentos:

            if cont == 1:
                fecha_final_b = lista.fecha_Emision_B
                fecha_final_0 = lista.fecha_Emision_0
                cont = 0

            else:
                fecha_actual_b = lista.fecha_Emision_B
                fecha_actual_0 = lista.fecha_Emision_0

                if abs((lista.fecha_Emision_B - fecha_final_b).days) <= 0:

                    fecha_final_b = lista.fecha_Emision_B

                if abs((lista.fecha_Emision_0 - fecha_final_0).days) >= 0:

                    fecha_final_0 = lista.fecha_Emision_0

        print(fecha_final_b)
        print(fecha_final_0)

        return lista_final

        ###################################################
        #                                                 #
        #                                                 #
        #   METODO PARA EXPLAYAR INFO                     #
        #                                                 #
        #                                                 #
        ###################################################

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lista_final'] = self.reporte_general()
        context['lista_emisiones'] = self.reporte_emisiones()
        context['lista_aprobadosConstruccion_documentos'] = self.reporte_aprobadosConstruccion_documentos()
        context['lista_total_documentos'] = self.reporte_total_documentos()
        context['lista_curva_s'] = self.reporte_curva_s_fechas()

        return context