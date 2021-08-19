from typing import Text
from django.db.models.query_utils import select_related_descend
from django.shortcuts import redirect, render
from django.urls import (reverse_lazy, reverse)
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from analitica.models import CurvasBase
from panel_carga.views import ProyectoMixin
from bandeja_es.models import Version
from panel_carga.models import Documento, Proyecto
from panel_carga.choices import ESTADO_CONTRATISTA, ESTADOS_CLIENTE, TYPES_REVISION
from datetime import datetime, timedelta, tzinfo
from django.contrib import messages
import requests
from django.utils import timezone
import math

# Create your views here.


class IndexAnalitica(ProyectoMixin, TemplateView):
    template_name =  'analitica/index.html'
    # def get_queryset(self):
    #     qs = Documento.objects.filter(proyecto=self.proyecto)
    #     return qs
    
    def get_queryset(self):
        qs1 = Documento.objects.filter(proyecto=self.proyecto)
        return qs1
 
    def get_versiones(self):
        user_roles = [4,5]
        qs1 = self.get_queryset()
        qs2 = Version.objects.select_related('documento_fk').filter(documento_fk__in=qs1, owner__perfil__rol_usuario__in=user_roles) #.select_related("owner").filter(owner__in=users)
        return qs2

    def get_versiones_last(self):
        qs1 = self.get_queryset()
        qs2 = Version.objects.select_related('documento_fk').filter(documento_fk__in=qs1) #.select_related("owner").filter(owner__in=users)
        return qs2

    ###################################################
    #                                                 #
    #                                                 #
    #   FUNCIONES GENERALES                           #
    #                                                 #
    #                                                 #
    ###################################################
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reporte_general = self.reporte_general()
        reporte_emisiones = self.reporte_emisiones()
        reporte_total_documentos_emitidos = self.reporte_total_documentos_emitidos()
        reporte_total_documentos = self.reporte_total_documentos()
        reporte_documentos_valido_contruccion = self.reporte_documentos_valido_contruccion()
        reporte_curva_s_avance_real = self.reporte_curva_s_avance_real()
        reporte_curva_s_avance_esperado = self.reporte_curva_s_avance_esperado()       
        reporte_curva_s_fechas = self.reporte_curva_s_fechas()

        context['lista_final'] = reporte_general
        context['lista_final_largo'] = len(reporte_general) 
        context['lista_emisiones'] = reporte_emisiones
        context['lista_emisiones_largo'] = len(reporte_emisiones) 
        context['lista_total_documentos_emitidos'] = reporte_total_documentos_emitidos
        context['lista_total_documentos_emitidos_largo'] = len(reporte_total_documentos_emitidos) 
        context['lista_total_documentos'] = reporte_total_documentos
        context['lista_total_documentos_largo'] = len(reporte_total_documentos) 
        context['validos_contruccion'] = reporte_documentos_valido_contruccion
        context['validos_contruccion_largo'] = len(reporte_documentos_valido_contruccion)
        context['tamano_grafico_uno'] = self.valor_eje_x_grafico_uno()
        context['espacios_grafico_uno'] = self.espacios_eje_x_grafico_uno()
        context['tamano_grafico_tres'] = self.valor_eje_x_grafico_tres()
        context['espacios_grafico_tres'] = self.espacios_eje_x_grafico_tres()
        context['lista_curva_s_avance_real'] = reporte_curva_s_avance_real
        context['lista_curva_s_avance_real_largo'] = len(reporte_curva_s_avance_real) 
        context['lista_curva_s_avance_esperado'] = reporte_curva_s_avance_esperado
        context['lista_curva_s_avance_esperado_largo'] = len(reporte_curva_s_avance_esperado) 
        context['lista_curva_s_fechas'] = reporte_curva_s_fechas
        context['lista_curva_s_fechas_largo'] = len(reporte_curva_s_fechas) 

        ## Opción 2
        qs = CurvasBase.objects.filter(proyecto=self.proyecto).last()
        context['curvaBase'] = qs
        return context
    
    def Obtener_documentos_versiones(self):

        lista_final = []
        lista_final_versiones = []
        lista_final_no_versiones = []
        lista_actual = []
        documentos = self.get_queryset()
        documentos_totales = len(documentos)
        versiones_documentos = self.get_versiones()
        version_final = 0

        #Obtener lista de las últimas versiones de cada documento
        if documentos_totales != 0:
            if versiones_documentos:
                for doc in documentos: 
                    comprobacion = 0
                    for version in versiones_documentos:
                        if str(doc.Codigo_documento) == str(version.documento_fk):
                            version_final = version
                            comprobacion = 1
                        
                    if comprobacion == 1:
                        lista_actual = [version_final, doc]
                        lista_final_versiones.append(lista_actual)
                    
                    if comprobacion == 0:
                        lista_final_no_versiones.append(doc)

                lista_final.append(lista_final_versiones)
                lista_final.append(lista_final_no_versiones)

            if not versiones_documentos:    
                pass

        else:
            lista_actual = [0,0] 
            lista_final.append(lista_actual)
            
        return lista_final

    def Obtener_documentos_versiones_tablas(self):

        documentos = self.get_queryset()
        documentos_totales = len(documentos)
        versiones_documentos = self.get_versiones_last()

        lista_final = []
        lista_inicial = []
        lista_final_versiones = []
        lista_final_no_versiones = []
        version_final = 0

        if documentos_totales != 0:
            if versiones_documentos != 0:
                for doc in documentos:
                    comprobacion = 0
                    for version in versiones_documentos:
                        if str(doc.Codigo_documento) == str(version.documento_fk):
                            version_final = version
                            comprobacion = 1

                    if comprobacion == 1:
                        lista_inicial = [version_final, doc]
                        lista_final_versiones.append(lista_inicial)
                    
                    if comprobacion == 0:
                        lista_final_no_versiones.append(doc)

                lista_final.append(lista_final_versiones)
                lista_final.append(lista_final_no_versiones)

            if not versiones_documentos:
                pass
        
        else:
            lista_actual = [0,0] 
            lista_final.append(lista_actual)
    
        return lista_final

    ###################################################
    #                                                 #
    #                                                 #
    #   PRIMER GRÁFICO DE ESTADOS DE LOS DOCUMENTOS   #
    #                                                 #
    #                                                 #
    ###################################################
    
    def reporte_general(self):

        lista_final = self.Obtener_documentos_versiones_tablas()

        estados_documento = []
        estados_final = []

        #Obtener lista de cantidad de documentos por tipo de versión
        if len(lista_final) != 0:
            for estado in TYPES_REVISION[1:]:
                cont = 0
                for lista in lista_final[0]:
                    estado_documento = lista[0].revision 
                    if estado_documento == estado[0]:
                        cont = cont + 1
                if cont != 0:
                    estados_documentos = [cont, estado[1]]
                    estados_final.append(estados_documentos)

        if len(lista_final) == 0:
            estados_documento = [0, 'Sin registros']
            estados_final.append(estados_documento)

        return estados_final

    ###################################################
    #                                                 #
    #                                                 #
    #   SEGUNDO GRÁFICO DE EMITIDOS POR SUBESTACION   #
    #                                                 #
    #                                                 #
    ###################################################

    def reporte_emisiones(self):
        
        lista_final = []

        aprobados_final = []
        aprobados_inicial = []
        documentos = self.get_queryset()
        documentos_totales = len(documentos)
        especialidad_list = tuple()
        versiones_documentos = self.Obtener_documentos_versiones_tablas()

        if documentos_totales != 0:
            if len(versiones_documentos[0]) != 0:
                #Obtener versiones que no poseen un estado de revisión
                for si_version in versiones_documentos[0]:
                    cont = 0
                    if si_version[0]:
                        for revision in TYPES_REVISION[1:]:

                            #Comparar que la versión no posea ningún estado de revisión
                            if revision[0] == si_version[0].revision:
                                cont = 1

                        #Almacena la versión que no posee estado de revisión
                        if cont == 0: 
                            lista_final.append(si_version[1])

                #Se almacenan los documentos sin versiones
                for no_version in versiones_documentos[1]:
                    lista_final.append(no_version)

            #Obtener lista de todas las especialidades
            for special in documentos:
                especialidad_actual = special.Especialidad
                if not especialidad_actual in especialidad_list:
                    especialidad_list = especialidad_list + (str(especialidad_actual),)

            #Obtener lista final de cantidad de versiones/documentos por especialidad pendientes
            for especialidad in especialidad_list:
                cont = 0  
                for lista in lista_final: 
                    mi_especialidad = lista.Especialidad
                    if mi_especialidad == especialidad:
                        cont = cont + 1
                if cont != 0:
                    aprobados_inicial = [cont, especialidad]
                    aprobados_final.append(aprobados_inicial)

        if documentos_totales == 0:
            aprobados_inicial = [0, 'Sin registros']
            aprobados_final.append(aprobados_inicial)

        return aprobados_final      

    ###################################################
    #                                                 #
    #                                                 #
    #   TERCER GRÁFICO DE STATUS POR ESPECIALIDAD     #
    #                                                 #
    #                                                 #
    ###################################################

    def reporte_total_documentos_emitidos(self):
        
        aprobados_final = []
        aprobados_inicial = []
        documentos = self.get_queryset()
        documentos_totales = len(documentos)
        especialidad_list = tuple()
        versiones_documentos = self.Obtener_documentos_versiones_tablas()

        if documentos_totales != 0:

            #Obtener lista de todas las especialidades
            for special in documentos:
                especialidad_actual = special.Especialidad
                if not especialidad_actual in especialidad_list:
                    especialidad_list = especialidad_list + (str(especialidad_actual),)

            #Obtener lista final de cantidad de versiones/documentos por especialidad emitidos
            for especialidad in especialidad_list:
                cont = 0 
                for lista in versiones_documentos[0]: 
                    mi_especialidad = lista[1].Especialidad
                    if mi_especialidad == especialidad:
                        cont = cont + 1
                if cont != 0:
                    aprobados_inicial = [cont, especialidad]
                    aprobados_final.append(aprobados_inicial) 

        if documentos_totales == 0:
            aprobados_inicial = [0, 'Sin registros']
            aprobados_final.append(aprobados_inicial)

        return aprobados_final

    def reporte_total_documentos(self):

        lista_actual = []
        lista_final = []

        documentos = self.get_queryset()
        documentos_totales = len(documentos)
        especialidad_list = tuple()

        if documentos_totales != 0:

            #Obtener lista de todas las especialidades 
            for special in documentos:
                especialidad_actual = special.Especialidad
                if not especialidad_actual in especialidad_list:
                    especialidad_list = especialidad_list + (str(especialidad_actual),)
            
            #Obtener documentos totales por especialidad
            for especialidad in especialidad_list:
                cont = 0 
                for lista in documentos: 
                    mi_especialidad = lista.Especialidad
                    if mi_especialidad == especialidad:
                        cont = cont + 1
                lista_actual = [cont, especialidad]
                lista_final.append(lista_actual)

        if documentos_totales == 0:
            lista_actual = [0, 'Sin registros']
            lista_final.append(lista_actual)
        
        return lista_final

    ###################################################
    #                                                 #
    #                                                 #
    #   CUARTO GRÁFICO DE STATUS POR ESPECIALIDAD     #
    #                                                 #
    #                                                 #
    ###################################################

    def reporte_documentos_valido_contruccion(self):

        lista_final = []
        documentos = self.get_queryset()
        documentos_totales = len(documentos)
        documentos_valido_contruccion = 0
        documentos_no_valido_contruccion = 0
        versiones_documentos = self.Obtener_documentos_versiones_tablas()
        
        if documentos_totales != 0:

            #Obtener lista de todas las especialidades 
            for version in versiones_documentos[0]:
                if version[0]:
                    estado_cliente = version[0].estado_cliente
                    if estado_cliente == 5:
                        documentos_valido_contruccion = documentos_valido_contruccion + 1
                    else:
                        documentos_no_valido_contruccion = documentos_no_valido_contruccion + 1
            
            documentos_no_valido_contruccion = documentos_no_valido_contruccion + len(versiones_documentos[1])

            lista_final.append(documentos_valido_contruccion)
            lista_final.append(documentos_no_valido_contruccion)

        if documentos_totales == 0:
            lista_final.append(0)
            lista_final.append(0)
        
        return lista_final

    ###################################################
    #                                                 #
    #                                                 #
    #   OBTENER VALORES DE LOS EJES                   #
    #                                                 #
    #                                                 #
    ###################################################

    def valor_eje_x_grafico_uno(self):

        #Llamado para un método definido anteriormente
        lista_grafico_uno = self.reporte_general()
        maximo = 0
        cont = 0

        #Se obtiene el valor máximo del gráfico
        for lista in lista_grafico_uno:
            if cont == 0:
                maximo = lista[0]
                cont = 1
            else:
                if maximo < lista[0]:
                    maximo = lista[0]
        
        #Se verífica que el maximo sea divisible por 10, para el caso de un maximo superior a 20
        division_exacta = 0
        if maximo > 20:  
            division_exacta = maximo % 10
            while division_exacta != 0:
                maximo = maximo + 1
                division_exacta = maximo % 10
        maximo = maximo + 1

        return maximo

    def espacios_eje_x_grafico_uno(self):

        #Llamado para un método definido anteriormente
        dividendo = self.valor_eje_x_grafico_uno() - 1
        espacios = 0

        #Se secciona el eje en 10 partes iguales
        if dividendo > 20:
            espacios = dividendo / 10
        else:
            espacios = 1

        return int(espacios)

    def valor_eje_x_grafico_tres(self):

        #Llamado para un método definido anteriormente
        lista_grafico_uno = self.reporte_total_documentos()
        maximo = 0
        cont = 0

        #Se obtiene el valor máximo del gráfico
        for lista in lista_grafico_uno:
            if cont == 0:
                maximo = lista[0]
                cont = 1       
            else:
                if maximo < lista[0]:
                    maximo = lista[0]
        
        #Se verífica que el maximo sea divisible por 10, para el caso de un maximo superior a 20
        division_exacta = 0
        if maximo > 20:  
            division_exacta = maximo % 10
            while division_exacta != 0:
                maximo = maximo + 1
                division_exacta = maximo % 10
        maximo = maximo + 1

        return maximo

    def espacios_eje_x_grafico_tres(self):

        #Llamado para un método definido anteriormente
        dividendo = self.valor_eje_x_grafico_tres() - 1
        espacios = 0

        #Se secciona el eje en 10 partes iguales
        if dividendo > 20:
            espacios = dividendo / 10
        else:
            espacios = 1

        return int(espacios)

    ###################################################
    #                                                 #
    #                                                 #
    #   GRÁFICO DE CURVA S                            #
    #                                                 #
    #                                                 #
    ###################################################

    def Obtener_fechas(self):
        elementos_final = []
        documentos = self.get_queryset()
        valor_ganado = len(documentos)
        curva_base = CurvasBase.objects.filter(proyecto=self.proyecto).last().datos_lista

        if valor_ganado !=0:

            if curva_base:

                valor_ganado = (100 / valor_ganado)

                #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
                fechas_controles = []
                
                #Obtener la ultima fecha de emisión en B y en 0
                fecha_emision_b = 0
                fecha_emision_0 = 0
                ultima_fecha_b = 0
                ultima_fecha_0 = 0
                ultima_de_dos = 0
                cont = 0

                #Obtener la primera fecha por documento
                primera_fecha_b = 0
                primera_fecha_0 = 0
                primera_de_dos = 0

                for doc in documentos:
                    if cont == 0:               
                        fecha_emision_b = doc.fecha_Emision_B
                        fecha_emision_0 = doc.fecha_Emision_0
                        ultima_fecha_b = fecha_emision_b
                        ultima_fecha_0 = fecha_emision_0
                        primera_fecha_b = doc.fecha_Emision_B
                        primera_fecha_0 = doc.fecha_Emision_0
                        cont = 1
                    
                    if cont != 0:   
                        fecha_emision_b = doc.fecha_Emision_B
                        fecha_emision_0 = doc.fecha_Emision_0
                        if fecha_emision_b > ultima_fecha_b:
                            ultima_fecha_b = fecha_emision_b
                        if fecha_emision_0 > ultima_fecha_0:                 
                            ultima_fecha_0 = fecha_emision_0
                        if fecha_emision_b < primera_fecha_b:               
                            primera_fecha_b = fecha_emision_b
                        if fecha_emision_0 < primera_fecha_0:            
                            primera_fecha_0 = fecha_emision_0

                #Verificar cuál de las dos fechas, emisión B y 0, es la última
                if ultima_fecha_b >= ultima_fecha_0:
                    ultima_de_dos = ultima_fecha_b
                if ultima_fecha_b < ultima_fecha_0:
                    ultima_de_dos = ultima_fecha_0
                if primera_fecha_b < primera_fecha_0:
                    primera_de_dos = primera_fecha_b
                if primera_fecha_b > primera_fecha_0:
                    primera_de_dos = primera_fecha_0

                primera_de_dos = primera_de_dos.replace(tzinfo = None)
                ultima_de_dos = ultima_de_dos.replace(tzinfo = None)

                primera_de_dos = primera_de_dos + timedelta(hours=23)
                primera_de_dos = primera_de_dos + timedelta(minutes=59)
                primera_de_dos = primera_de_dos + timedelta(seconds=59)

                largo_fecha = 19
                contador_menor = 0
                contador_mayor = 0
                nueva_fecha_menor = ''
                nueva_fecha_mayor = ''

                for menor in curva_base[1]:
                    if contador_menor < largo_fecha:
                        nueva_fecha_menor = nueva_fecha_menor + menor
                    contador_menor = contador_menor + 1

                for mayor in curva_base[len(curva_base)-1]:
                    if contador_mayor < largo_fecha:
                        nueva_fecha_mayor = nueva_fecha_mayor + mayor
                    contador_mayor = contador_mayor + 1

                primera_curva_base = datetime.strptime(nueva_fecha_menor, '%Y-%m-%d %H:%M:%S')
                ultima_curva_base = datetime.strptime(nueva_fecha_mayor, '%Y-%m-%d %H:%M:%S')      

                #Verificar si la curva base posee la primera fecha de los documentos
                if primera_curva_base > primera_de_dos:
                    diferencia = abs((primera_curva_base - primera_de_dos).days)  
                    contador = 0 
                    semanas = 0    
                    resultado = diferencia

                    #Se obtienen las semanas iniciales para agregar
                    while resultado != 0:
                        resultado = diferencia % 7
                        contador = contador + 1
                        diferencia = diferencia + 1
                    
                    #Se agrega una fecha extra final
                    contador = contador + 1

                    #Se agregan los semanas al arreglo de fechas
                    while contador != 0:
                        semanas = contador * 7
                        nueva_semana = primera_curva_base - timedelta(days=semanas)
                        fechas_controles.append(nueva_semana)
                        contador = contador - 1
                
                #Almacenar fechas faltantes
                contador_fechas = 0
                for controles in curva_base:
                    if (contador_fechas%2) != 0:
                        cont = 0
                        nueva_fecha = ''
                        for menor in controles:
                            if cont < largo_fecha:
                                nueva_fecha = nueva_fecha + menor
                            cont = cont + 1
                        
                        fecha_agregar = datetime.strptime(nueva_fecha, '%Y-%m-%d %H:%M:%S')
                        fechas_controles.append(fecha_agregar)
                    contador_fechas = contador_fechas + 1
               
                #Verificar si la curva base posee la última fecha de los documentos
                if ultima_curva_base < ultima_de_dos:    
                    diferencia = abs((ultima_curva_base - primera_de_dos).days)
                    contador = 0 
                    semanas = 0    
                    resultado = diferencia

                    #Se obtienen las semanas iniciales para agregar
                    while resultado != 0:
                        resultado = diferencia % 7
                        contador = contador + 1
                        diferencia = diferencia + 1
                    
                    #Se agrega una fecha extra final
                    contador = contador + 1

                    #Se agregan los semanas al arreglo de fechas
                    while semanas != contador:
                        semanas = semanas + 1
                        semanas_final = semanas*7
                        nueva_semana = ultima_curva_base + timedelta(days=semanas_final)
                        fechas_controles.append(nueva_semana)

                #Se almacena arreglo de fechas en la lista final
                elementos = []
                elementos_final = []
                elementos = [fechas_controles]
                elementos_final.append(elementos)

            if  not curva_base:

                valor_ganado = (100 / valor_ganado)

                #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
                fechas_controles = []
                
                #Obtener la ultima fecha de emisión en B y en 0
                fecha_emision_b = 0
                fecha_emision_0 = 0
                ultima_fecha_b = 0
                ultima_fecha_0 = 0
                ultima_de_dos = 0
                cont = 0

                #Obtener la primera fecha por documento
                primera_fecha_b = 0
                primera_fecha_0 = 0
                primera_de_dos = 0

                for doc in documentos:
                    if cont == 0:               
                        fecha_emision_b = doc.fecha_Emision_B
                        fecha_emision_0 = doc.fecha_Emision_0
                        ultima_fecha_b = fecha_emision_b
                        ultima_fecha_0 = fecha_emision_0
                        primera_fecha_b = doc.fecha_Emision_B
                        primera_fecha_0 = doc.fecha_Emision_0
                        cont = 1
                    
                    if cont != 0:   
                        fecha_emision_b = doc.fecha_Emision_B
                        fecha_emision_0 = doc.fecha_Emision_0
                        if fecha_emision_b > ultima_fecha_b:
                            ultima_fecha_b = fecha_emision_b
                        if fecha_emision_0 > ultima_fecha_0:                 
                            ultima_fecha_0 = fecha_emision_0
                        if fecha_emision_b < primera_fecha_b:               
                            primera_fecha_b = fecha_emision_b
                        if fecha_emision_0 < primera_fecha_0:            
                            primera_fecha_0 = fecha_emision_0

                #Verificar cuál de las dos fechas, emisión B y 0, es la última
                if ultima_fecha_b >= ultima_fecha_0:
                    ultima_de_dos = ultima_fecha_b
                if ultima_fecha_b < ultima_fecha_0:
                    ultima_de_dos = ultima_fecha_0
                if primera_fecha_b < primera_fecha_0:
                    primera_de_dos = primera_fecha_b
                if primera_fecha_b > primera_fecha_0:
                    primera_de_dos = primera_fecha_0

                primera_de_dos = primera_de_dos.replace(tzinfo = None)
                ultima_de_dos = ultima_de_dos.replace(tzinfo = None)

                #Agregar una semana antes a la primera de los documentos
                fechas_controles = []
                primera_de_dos = primera_de_dos + timedelta(hours=23)
                primera_de_dos = primera_de_dos + timedelta(minutes=59)
                primera_de_dos = primera_de_dos + timedelta(seconds=59)

                primera_de_dos = primera_de_dos - timedelta(days=7)
                fechas_controles.append(primera_de_dos)
                primera_de_dos = primera_de_dos + timedelta(days=7)
                fechas_controles.append(primera_de_dos)

                #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
                fecha_actual = primera_de_dos
                fecha_posterior = fecha_actual + timedelta(days=7)
                
                #Se almacenan semana a semana hasta curbrir la fecha de termino del proyecto
                while fecha_actual < ultima_de_dos and fecha_posterior < ultima_de_dos:
                    fecha_actual = fecha_actual + timedelta(days=7)
                    fecha_posterior = fecha_actual + timedelta(days=7)
                    fechas_controles.append(fecha_actual)
                fechas_controles.append(ultima_de_dos)

                #Se almacena arreglo de fechas en la lista final
                elementos = []
                elementos_final = []
                elementos = [fechas_controles]
                elementos_final.append(elementos)

        else:
            #Se almacena arreglo de fechas en la lista final
            elementos = []
            elementos_final = ['Sin registro']
            elementos_final.append(elementos)
        
        return elementos_final

    def reporte_curva_s_avance_real(self):

        documentos = self.get_queryset()
        valor_ganado = len(documentos)
        lista_final = self.Obtener_fechas()
        dia_actual = timezone.now()
        dia_actual = dia_actual.replace(tzinfo = None)
        versiones_documentos = self.get_versiones()
        
        if valor_ganado !=0:

            #Variables
            valor_ganado = (100 / valor_ganado)                  
            avance_inicial = []
            avance_final = []
            fecha_version = 0
            fechas_controles = lista_final[0][0]
            avance_fechas_controles = []
            contador_versiones = 0
            fechas_controles_recorrer = []
            ultima_fecha = 0
            contador_fechas = 1
            lista_versiones = []

            #Variables final
            largo_inicial_fechas = len(fechas_controles)
            largo_necesitado = 0

            #Se recorren las fechas de control para guardar las que necesitan evaluarse
            for fechas in fechas_controles:
                if fechas <= dia_actual:
                    fechas_controles_recorrer.append(fechas)
                    avance_fechas_controles.append(0)
                else:
                    if fechas > dia_actual and contador_fechas == 1:
                        fechas_controles_recorrer.append(fechas)
                        avance_fechas_controles.append(0)
                        contador_fechas = 0
                ultima_fecha = fechas

            #Se almacenan los dato del documento
            for doc in documentos:
                cont = 0
                cont2 = 0
                for versiones in versiones_documentos:
                    if str(doc.Codigo_documento) == str(versiones.documento_fk):
                        if versiones.revision < 5 and cont == 0:               
                            version_letras = versiones
                            cont = 1
                        if versiones.revision > 4:             
                            version_numerica = versiones
                            cont2 = 1

                if cont == 1 and cont2 == 1:
                    lista_versiones.append([doc, [version_letras, version_numerica]])

                if cont == 1 and cont2 == 0:
                    lista_versiones.append([doc, [version_letras]])

                if cont == 0 and cont2 == 1:
                    lista_versiones.append([doc, [version_numerica]])

            #Se recorren las versiones a calcular el avance real
            for docs in lista_versiones:
                contador_avance = 0

                for versiones in docs[1]:
                    contador_versiones = contador_versiones + 1
                    fecha_version = versiones.fecha.replace(tzinfo=None)
                    revision_documento = versiones.revision
                    valor_documento = 0
                    cont = 0

                    #Se calcula el avance real en la fecha de control que corresponda
                    for controles in fechas_controles_recorrer:
                        if valor_documento == 0:
                            calculo_real_0 = 0
                            calculo_real_b = 0
                            avance_documento = 0

                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                            for revision in TYPES_REVISION[1:4]:
                                if revision[0] == revision_documento and fecha_version <= controles:
                                    calculo_real_b = valor_ganado * 0.7
                                if cont == (len(fechas_controles) - 1):
                                    if revision[0] == revision_documento and fecha_version > controles:                              
                                        calculo_real_b = valor_ganado * 0.7

                            if contador_avance == 0:
                                #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                for revision in TYPES_REVISION[5:]:
                                    if revision[0] == revision_documento and fecha_version <= controles:
                                        calculo_real_0 = valor_ganado * 1
                                    if cont == (len(fechas_controles) - 1):
                                        if revision[0] == revision_documento and fecha_version > controles:                                
                                            calculo_real_0 = valor_ganado * 1

                            if contador_avance != 0:
                                #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                for revision in TYPES_REVISION[5:]:
                                    if revision[0] == revision_documento and fecha_version <= controles:
                                        calculo_real_0 = valor_ganado * 0.3
                                    if cont == (len(fechas_controles) - 1):
                                        if revision[0] == revision_documento and fecha_version > controles:                                
                                            calculo_real_0 = valor_ganado * 0.3

                            #Se comparan los avances en emision b y 0, para guardar el mayor valor
                            if calculo_real_b > calculo_real_0:
                                avance_documento = calculo_real_b                               

                            #Se comparan los avances en emision b y 0, para guardar el mayor valor
                            if calculo_real_b < calculo_real_0:
                                avance_documento = calculo_real_0

                            #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
                            if avance_documento != 0:
                                avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
                                valor_documento = 1 
                                contador_avance = contador_avance + 1
                            cont = cont + 1

            if contador_versiones != 0:
                #Se calcula el avance real por fecha de control, mediante las sumatorias de estas, cubriendo las fechas de controles hasta el día actual
                contador_final = 0
                calculo_avance_final = 0
                largo_fechas = len(avance_fechas_controles)
                
                for avance in avance_fechas_controles: 
                    if contador_final < largo_fechas:
                        calculo_avance_final = calculo_avance_final + avance
                        avance_inicial = [format(calculo_avance_final, '.2f'), 0]
                        avance_final.append(avance_inicial)
                        contador_final = contador_final + 1

                #Funcion en caso de que el avance real no sea el 100%
                diferencia_arreglo_fecha = len(fechas_controles) - largo_fechas
                diferencia = 100 - calculo_avance_final
                avance_semanal = calculo_avance_final/(largo_fechas - 1)

                if calculo_avance_final == 100:
                    #Se calcula el avance porcentual
                    largo_curva_s = len(avance_final)
                    contador_curva_s = 1
                    diferencia = 0
                    arreglo_valores = []
                    arreglo_valores_final = []

                    arreglo_valores = [avance_final[0][0], avance_final[0][1], '0.0']
                    arreglo_valores_final.append(arreglo_valores)

                    while contador_curva_s < largo_curva_s:
                        if avance_final[contador_curva_s][1] == 0:
                            diferencia = float(avance_final[contador_curva_s][0]) - float(avance_final[contador_curva_s - 1][0])
                            diferencia = format(diferencia, '.2f')
                            arreglo_valores = [avance_final[contador_curva_s][0], avance_final[contador_curva_s][1], str(diferencia)]
                            arreglo_valores_final.append(arreglo_valores)
                        else:
                            diferencia = float(avance_final[contador_curva_s][0]) - float(avance_final[contador_curva_s - 1][0])
                            diferencia = format(diferencia, '.2f')
                            arreglo_valores = [avance_final[contador_curva_s][0], avance_final[contador_curva_s][1], str(diferencia)]
                            arreglo_valores_final.append(arreglo_valores)
                        contador_curva_s = contador_curva_s + 1                                                                                       

                    #Se almacena avance real en lista final
                    avance_final = arreglo_valores_final
                
                if avance_semanal != 0:
                    proyeccion = (diferencia / avance_semanal) - diferencia_arreglo_fecha
                    contador = 0

                    if  calculo_avance_final < 100 and calculo_avance_final > 0:

                        #Variables
                        avance_inicial_dos = []
                        avance_final_dos = []
                        avance_fechas_controles = []
                        fechas_controles_recorrer = []
                        contador_versiones = 0
                        contador_fechas = 1

                        #Funcion para agregar nuevas fechas
                        while contador < proyeccion:
                            ultima_fecha = ultima_fecha + timedelta(days=7)
                            fechas_controles.append(ultima_fecha)
                            contador = contador + 1

                        #Se recorren las fechas de control para guardar las que necesitan evaluarse
                        for fechas in fechas_controles:
                            if fechas <= dia_actual:
                                fechas_controles_recorrer.append(fechas)
                                avance_fechas_controles.append(0)
                            else:
                                if fechas > dia_actual and contador_fechas == 1:
                                    fechas_controles_recorrer.append(fechas)
                                    avance_fechas_controles.append(0)
                                    contador_fechas = 0

                        #Se recorren las versiones a calcular el avance real
                        for docs in lista_versiones:
                            contador_avance = 0

                            for versiones in docs[1]:
                                contador_versiones = contador_versiones + 1
                                fecha_version = versiones.fecha.replace(tzinfo=None)
                                revision_documento = versiones.revision
                                valor_documento = 0
                                cont = 0

                                #Se calcula el avance real en la fecha de control que corresponda
                                for controles in fechas_controles_recorrer:
                                    if valor_documento == 0:
                                        calculo_real_0 = 0
                                        calculo_real_b = 0
                                        avance_documento = 0

                                        #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                        for revision in TYPES_REVISION[1:4]:
                                            if revision[0] == revision_documento and fecha_version <= controles:
                                                calculo_real_b = valor_ganado * 0.7
                                            if cont == (len(fechas_controles) - 1):
                                                if revision[0] == revision_documento and fecha_version > controles:                              
                                                    calculo_real_b = valor_ganado * 0.7

                                        if contador_avance == 0:
                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                            for revision in TYPES_REVISION[5:]:
                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                    calculo_real_0 = valor_ganado * 1
                                                if cont == (len(fechas_controles) - 1):
                                                    if revision[0] == revision_documento and fecha_version > controles:                                
                                                        calculo_real_0 = valor_ganado * 1

                                        if contador_avance != 0:
                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                            for revision in TYPES_REVISION[5:]:
                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                    calculo_real_0 = valor_ganado * 0.3
                                                if cont == (len(fechas_controles) - 1):
                                                    if revision[0] == revision_documento and fecha_version > controles:                                
                                                        calculo_real_0 = valor_ganado * 0.3

                                        #Se comparan los avances en emision b y 0, para guardar el mayor valor
                                        if calculo_real_b > calculo_real_0:
                                            avance_documento = calculo_real_b                               

                                        #Se comparan los avances en emision b y 0, para guardar el mayor valor
                                        if calculo_real_b < calculo_real_0:
                                            avance_documento = calculo_real_0

                                        #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
                                        if avance_documento != 0:
                                            avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
                                            valor_documento = 1 
                                            contador_avance = contador_avance + 1
                                        cont = cont + 1

                        #Se calcula el avance real por fecha de control, mediante las sumatorias de estas, cubriendo las fechas de controles hasta el día actual
                        contador_final = 0
                        calculo_avance_final = 0
                        largo_fechas = len(avance_fechas_controles)
                        
                        for avance in avance_fechas_controles: 
                            if contador_final < largo_fechas:
                                calculo_avance_final = calculo_avance_final + avance
                                avance_inicial_dos = [format(calculo_avance_final, '.2f'), 0]
                                avance_final_dos.append(avance_inicial_dos)
                                contador_final = contador_final + 1

                        #Funcion en caso de que el avance real no sea el 100%
                        diferencia_arreglo_fecha = len(fechas_controles) - largo_fechas
                        diferencia = 100 - calculo_avance_final
                        avance_semanal = calculo_avance_final/(largo_fechas - 1)
                        proyeccion = (diferencia / avance_semanal)
                        contador = 0

                        proyeccion = math.ceil(proyeccion)
                        if  calculo_avance_final < 100 and calculo_avance_final > 0:
                            while contador < proyeccion:
                                if contador == (proyeccion - 1):
                                    calculo_avance_final = 100
                                    avance_inicial_dos = [format(calculo_avance_final, '.2f'), 1]
                                    avance_final_dos.append(avance_inicial_dos)
                                    contador = contador + 1

                                else:
                                    calculo_avance_final = calculo_avance_final + avance_semanal
                                    avance_inicial_dos = [format(calculo_avance_final, '.2f'), 1]
                                    avance_final_dos.append(avance_inicial_dos)
                                    contador = contador + 1

                        #Se calcula el avance porcentual
                        largo_curva_s = len(avance_final_dos)
                        contador_curva_s = 1
                        diferencia = 0
                        arreglo_valores = []
                        arreglo_valores_final = []

                        arreglo_valores = [avance_final_dos[0][0], avance_final_dos[0][1], '0.0']
                        arreglo_valores_final.append(arreglo_valores)

                        while contador_curva_s < largo_curva_s:
                            if avance_final_dos[contador_curva_s][1] == 0:
                                diferencia = float(avance_final_dos[contador_curva_s][0]) - float(avance_final_dos[contador_curva_s - 1][0])
                                diferencia = format(diferencia, '.2f')
                                arreglo_valores = [avance_final_dos[contador_curva_s][0], avance_final_dos[contador_curva_s][1], str(diferencia)]
                                arreglo_valores_final.append(arreglo_valores)
                            else:
                                diferencia = float(avance_final_dos[contador_curva_s][0]) - float(avance_final_dos[contador_curva_s - 1][0])
                                diferencia = format(diferencia, '.2f')
                                arreglo_valores = [avance_final_dos[contador_curva_s][0], avance_final_dos[contador_curva_s][1], str(diferencia)]
                                arreglo_valores_final.append(arreglo_valores)
                            contador_curva_s = contador_curva_s + 1                                                                                       

                        #Se almacena avance real en lista final
                        avance_final = arreglo_valores_final

                        #Calcular extension de fechas
                        largo_necesitado = largo_fechas + proyeccion
                        largo_necesitado = largo_necesitado - largo_inicial_fechas
    
            if contador_versiones == 0:
                avance_inicial = [0]
                avance_final.append(avance_inicial)

        #Si no existen documentos, se almacenan valores vacios en el arreglo final
        if valor_ganado == 0:
               avance_inicial = []
               avance_final = []
               avance_inicial = [valor_ganado]
               avance_final.append(avance_inicial)

        return avance_final

    def reporte_curva_s_avance_esperado(self):
                
        lista_final = self.Obtener_fechas()
        documentos = self.get_queryset()
        valor_ganado = len(documentos)
        avance_esperado = []
        lista_final_esperado = []
        diferencia = 0
        
        if valor_ganado != 0:
            
            #Calculo del avance esperado por fecha de control
            fecha_emision_b = 0
            fecha_emision_0 = 0
            fechas_controles = lista_final[0][0]
            valor_ganado = (100 / valor_ganado)
            contador_largo = 0

            for controles in fechas_controles:
                if contador_largo < len(fechas_controles):
                    calculo_avanceEsperado = 0
                    for doc in documentos:                  
                        fecha_emision_b = doc.fecha_Emision_B.replace(tzinfo=None)
                        fecha_emision_0 = doc.fecha_Emision_0.replace(tzinfo=None)

                        #Se calcula el avance esperado mediante la comparación de la fecha de control y la fecha de emisión en B - 0
                        if fecha_emision_b <= controles and fecha_emision_0 > controles:
                            calculo_avanceEsperado = valor_ganado * 0.7 + calculo_avanceEsperado                      
                        if fecha_emision_0 <= controles and fecha_emision_b < controles:
                            calculo_avanceEsperado = valor_ganado * 1 + calculo_avanceEsperado

                    #Se almacena el avance esperado hasta la fecha de control
                    avance_esperado = [format(calculo_avanceEsperado, '.2f')]
                    lista_final_esperado.append(avance_esperado)
            
            calculo_parcial = []
            calculo_parcial_final = []
            contador_parcial = 1

            calculo_parcial = [lista_final_esperado[0][0], '0.0']
            calculo_parcial_final.append(calculo_parcial)

            while contador_parcial < len(lista_final_esperado):
                diferencia = float(lista_final_esperado[contador_parcial][0]) - float(lista_final_esperado[contador_parcial - 1][0])
                diferencia = format(diferencia, '.2f')
                calculo_parcial = [lista_final_esperado[contador_parcial][0], str(diferencia)]
                calculo_parcial_final.append(calculo_parcial)
                contador_parcial = contador_parcial + 1

            lista_final_esperado = calculo_parcial_final

        if valor_ganado == 0:
            avance_esperado = [int(valor_ganado)]
            lista_final_esperado.append(avance_esperado)


        return lista_final_esperado

    def reporte_curva_s_fechas(self):
        
        lista_final = self.Obtener_fechas()
        valor_ganado = self.get_queryset().count()
        lista_avance_real = self.reporte_curva_s_avance_real()
        fechas_controles = lista_final[0][0]
        diferencia = 0
        contador = 0
        ultima_fecha = 0

        if valor_ganado !=0:

            diferencia = len(lista_avance_real) - len(fechas_controles)
            
            if diferencia > 0:
                for fechas in fechas_controles:
                    ultima_fecha = fechas

                while contador < diferencia:
                    ultima_fecha = ultima_fecha + timedelta(days=7)
                    fechas_controles.append(ultima_fecha)
                    contador = contador + 1 

        if valor_ganado == 0:         
            fechas_controles = ['Sin registros']
            fechas_controles.append(fechas_controles)


        return fechas_controles           

    ###################################################
    #                                                 #
    #                                                 #
    #            METODO PARA EXPLAYAR INFO            #
    #                                                 #
    #                                                 #
    ###################################################

class CurvaBaseView(ProyectoMixin, TemplateView):

    http_method_names = ['get', 'post']
    template_name = 'analitica/curva_base.html'

    def Obtener_fechas(self):
        elementos_final = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        if valor_ganado !=0:

            valor_ganado = (100 / valor_ganado)
            documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

            #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
            fechas_controles = []
            
            #Obtener la ultima fecha de emisión en B y en 0
            fecha_emision_b = 0
            fecha_emision_0 = 0
            ultima_fecha_b = 0
            ultima_fecha_0 = 0
            ultima_de_dos = 0
            cont = 0

            #Obtener la primera fecha por documento
            primera_fecha_b = 0
            primera_fecha_0 = 0
            primera_de_dos = 0

            for doc in documentos:
                if cont == 0:               
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0
                    ultima_fecha_b = fecha_emision_b
                    ultima_fecha_0 = fecha_emision_0
                    primera_fecha_b = doc.fecha_Emision_B
                    primera_fecha_0 = doc.fecha_Emision_0
                    cont = 1
                
                if cont != 0:   
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0
                    if fecha_emision_b > ultima_fecha_b:
                        ultima_fecha_b = fecha_emision_b
                    if fecha_emision_0 > ultima_fecha_0:                 
                        ultima_fecha_0 = fecha_emision_0
                    if fecha_emision_b < primera_fecha_b:               
                        primera_fecha_b = fecha_emision_b
                    if fecha_emision_0 < primera_fecha_0:            
                        primera_fecha_0 = fecha_emision_0

            #Verificar cuál de las dos fechas, emisión B y 0, es la última
            if ultima_fecha_b >= ultima_fecha_0:
                ultima_de_dos = ultima_fecha_b
            if ultima_fecha_b < ultima_fecha_0:
                ultima_de_dos = ultima_fecha_0
            if primera_fecha_b < primera_fecha_0:
                primera_de_dos = primera_fecha_b
            if primera_fecha_b > primera_fecha_0:
                primera_de_dos = primera_fecha_0

            #Agregar una semana antes a la primera de los documentos
            fechas_controles = []
            primera_de_dos = primera_de_dos + timedelta(hours=23)
            primera_de_dos = primera_de_dos + timedelta(minutes=59)
            primera_de_dos = primera_de_dos + timedelta(seconds=59)
            primera_de_dos = primera_de_dos - timedelta(days=7)
            fechas_controles.append(primera_de_dos)
            primera_de_dos = primera_de_dos + timedelta(days=7)
            fechas_controles.append(primera_de_dos)

            #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
            fecha_actual = primera_de_dos
            fecha_posterior = fecha_actual + timedelta(days=7)
            
            #Se almacenan semana a semana hasta curbrir la fecha de termino del proyecto
            while fecha_actual < ultima_de_dos and fecha_posterior < ultima_de_dos:
                fecha_actual = fecha_actual + timedelta(days=7)
                fecha_posterior = fecha_actual + timedelta(days=7)
                fechas_controles.append(fecha_actual)
            fechas_controles.append(ultima_de_dos)

            #Se almacena arreglo de fechas en la lista final
            elementos = []
            elementos_final = []
            elementos = [fechas_controles]
            elementos_final.append(elementos)

        else:
            #Se almacena arreglo de fechas en la lista final
            elementos = []
            elementos_final = ['Sin registro']
            elementos_final.append(elementos)
        
        return elementos_final

    def Obtener_linea_base(self):
                
        lista_final = self.Obtener_fechas()
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        avance_esperado = []
        lista_final_esperado = []
        
        if valor_ganado != 0:
            
            #Calculo del avance esperado por fecha de control
            fecha_emision_b = 0
            fecha_emision_0 = 0
            fechas_controles = lista_final[0][0]
            valor_ganado = (100 / valor_ganado)
            contador_largo = 0

            for controles in fechas_controles:
                if contador_largo < len(fechas_controles):
                    calculo_avanceEsperado = 0
                    for doc in documentos:                  
                        fecha_emision_b = doc.fecha_Emision_B
                        fecha_emision_0 = doc.fecha_Emision_0

                        #Se calcula el avance esperado mediante la comparación de la fecha de control y la fecha de emisión en B - 0
                        if fecha_emision_b <= controles and fecha_emision_0 > controles:
                            calculo_avanceEsperado = valor_ganado * 0.7 + calculo_avanceEsperado                      
                        if fecha_emision_0 <= controles and fecha_emision_b < controles:
                            calculo_avanceEsperado = valor_ganado * 1 + calculo_avanceEsperado

                    #Se almacena el avance esperado hasta la fecha de control
                    avance_esperado = format(calculo_avanceEsperado, '.2f')
                    lista_final_esperado.append(avance_esperado)
                    lista_final_esperado.append(controles)


        if valor_ganado == 0:
            avance_esperado = [int(valor_ganado)]
            lista_final_esperado.append(avance_esperado)

        return lista_final_esperado

    def get_queryset(self, request, *args, **kwargs):
        qs = CurvasBase.objects.filter(proyecto=self.proyecto)
        return qs

    def post(self, request, *args, **kwargs):
        value = self.Obtener_linea_base()
        curva = CurvasBase(
            datos_lista= value,
            proyecto= self.proyecto
        )
        curva.save()
        messages.success(request, message="Curva base Guardada con éxito.")
        return redirect('PanelCarga')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        qs = CurvasBase.objects.filter(proyecto=self.proyecto).last()
        context['curvaBase'] = qs
        return self.render_to_response(context)
        