from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from bandeja_es.models import Version
from panel_carga.models import Documento, Proyecto
from panel_carga.choices import ESTADO_CONTRATISTA, ESTADOS_CLIENTE, TYPES_REVISION
from datetime import datetime, timedelta
from django.utils import timezone
import math

# Create your views here.


class IndexAnalitica(ProyectoMixin, TemplateView):
    template_name =  'analitica/index.html'
    ###################################################
    #                                                 #
    #                                                 #
    #   FUNCIONES GENERALES                           #
    #                                                 #
    #                                                 #
    ###################################################
    
    def Obtener_documentos_versiones(self):

        lista_final = []
        lista_actual = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        #Obtener lista de las últimas versiones de cada documento
        if documentos_totales != 0:
            for doc in documentos: 
                versiones = Version.objects.filter(documento_fk=doc).last()
                if versiones:         
                    lista_actual = [versiones, doc]
                    lista_final.append(lista_actual)
                if not versiones:    
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

        lista_final = self.Obtener_documentos_versiones()
        estados_documento = []
        estados_final = []
        documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        #Obtener lista de cantidad de documentos por tipo de versión
        if documentos_totales != 0:
            estado_documento = 0
            for estado in TYPES_REVISION[1:]:
                cont = 0
                for lista in lista_final:
                    estado_documento = lista[0].revision 
                    if estado_documento == estado[0]:
                        cont = cont + 1
                if cont != 0:
                    estados_documentos = [cont, estado[1]]
                    estados_final.append(estados_documentos)
        if documentos_totales == 0:
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
        
        lista_actual = []
        lista_final = []

        aprobados_final = []
        aprobados_inicial = []

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        especialidad_list = tuple()

        if documentos_totales != 0:

            #Obtener versiones que no poseen un estado de revisión
            for doc in documentos:
                versiones = Version.objects.filter(documento_fk=doc).last()
                if versiones:
                    cont = 0
                    for revision in TYPES_REVISION[1:]:

                        #Comparar que la versión no posea ningún estado de revisión
                        if revision[0] == versiones.revision:
                            cont = 1

                    #Almacena la versión que no posee estado de revisión
                    if cont == 0:
                        lista_actual = [versiones, doc] 
                        lista_final.append(lista_actual)
                if not versiones:
                    lista_actual = [versiones, doc] 
                    lista_final.append(lista_actual)

            #Obtener lista de todas las especialidades
            for lista in lista_final: 
                for special in documentos:
                    especialidad_actual = special.Especialidad
                    if not especialidad_actual in especialidad_list:
                        especialidad_list = especialidad_list + (str(especialidad_actual),)

            #Obtener lista final de cantidad de versiones/documentos por especialidad pendientes
            for especialidad in especialidad_list:
                cont = 0  
                for lista in lista_final: 
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

    ###################################################
    #                                                 #
    #                                                 #
    #   TERCER GRÁFICO DE STATUS POR ESPECIALIDAD     #
    #                                                 #
    #                                                 #
    ###################################################

    def reporte_total_documentos_emitidos(self):
        
        lista_actual = []
        lista_final = []

        aprobados_final = []
        aprobados_inicial = []

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        especialidad_list = tuple()

        if documentos_totales != 0:

            #Obtener lista de versiones que poseen un estado de revisión
            for doc in documentos:
                versiones = Version.objects.filter(documento_fk=doc).last()
                if versiones:
                    cont = 0
                    for revision in TYPES_REVISION[1:]:
                        
                        #Comparar versiones que si poseen un estado de revisión
                        if revision[0] == versiones.revision:
                            cont = 1
                    
                    #Almacena las versiones que poseen un estado de revisión
                    if cont == 1:
                        lista_actual = [versiones, doc] 
                        lista_final.append(lista_actual)

            #Obtener lista de todas las especialidades
            for lista in lista_final: 
                for special in documentos:
                    especialidad_actual = special.Especialidad
                    if not especialidad_actual in especialidad_list:
                        especialidad_list = especialidad_list + (str(especialidad_actual),)

            #Obtener lista final de cantidad de versiones/documentos por especialidad emitidos
            for especialidad in especialidad_list:
                cont = 0 
                for lista in lista_final: 
                    mi_especialidad = lista[1].Especialidad
                    if mi_especialidad == especialidad:
                        cont = cont + 1
                aprobados_inicial = [cont, especialidad]
                aprobados_final.append(aprobados_inicial) 

        if documentos_totales == 0:
            aprobados_inicial = [0, 'Sin registros']
            aprobados_final.append(aprobados_inicial)

        return aprobados_final

    def reporte_total_documentos(self):

        lista_actual = []
        lista_final = []

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
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
        #   CUARTO GRÁFICO DE CURVA S                     #
        #                                                 #
        #                                                 #
        ###################################################

    def Obtener_fechas(self):
        elementos_final = []
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        dia_actual = timezone.now()

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
            primera_de_dos = primera_de_dos - timedelta(days=7)
            fechas_controles.append(primera_de_dos)
            primera_de_dos = primera_de_dos + timedelta(days=7)
            fechas_controles.append(primera_de_dos)

            #Obtener fechas de inicio y termino de proyecto
            semana_actual = timezone.now()

            #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
            fecha_actual = primera_de_dos
            fecha_posterior = fecha_actual + timedelta(days=7)
            
            #Se almacenan semana a semana hasta curbrir la fecha de termino del proyecto
            while fecha_actual < ultima_de_dos and fecha_posterior < ultima_de_dos:
                if fecha_actual < dia_actual and dia_actual < fecha_posterior:
                    fechas_controles.append(dia_actual)
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
            elementos_final = ['Sin registros']
            elementos_final.append(elementos)
        
        return elementos_final

    def reporte_curva_s_avance_real(self):

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        lista_final = self.Obtener_fechas()
        dia_actual = timezone.now()
        
        if valor_ganado !=0:

            #Variables
            valor_ganado = (100 / valor_ganado)                     
            avance_inicial = []
            avance_final = []
            fecha_version = 0
            fecha_documento = 0
            fechas_controles = lista_final[0][0]
            avance_fechas_controles = []
            contador_versiones = 0
            fechas_controles_recorrer = []
            ultima_fecha = 0

            #Variables final
            largo_inicial_fechas = len(fechas_controles)
            largo_necesitado = 0

            #Se recorren las fechas de control para guardar las que necesitan evaluarse
            for fechas in fechas_controles:
                if fechas <= dia_actual:
                    fechas_controles_recorrer.append(fechas)
                    avance_fechas_controles.append(0)
                ultima_fecha = fechas

            #Se almacenan los dato del documento
            for doc in documentos:
                fecha_emision_0 = doc.fecha_Emision_0
                fecha_emision_b = doc.fecha_Emision_B
                versiones = Version.objects.filter(documento_fk=doc).last()
                cont = 0

                #Si exite una version
                if versiones:
                    contador_versiones = contador_versiones + 1
                    fecha_version = versiones.fecha
                    revision_documento = versiones.revision
                    valor_documento = 0

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

                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                            for revision in TYPES_REVISION[5:]:
                                if revision[0] == revision_documento and fecha_version <= controles:
                                    calculo_real_0 = valor_ganado * 1
                                if cont == (len(fechas_controles) - 1):
                                    if revision[0] == revision_documento and fecha_version > controles:                                
                                        calculo_real_0 = valor_ganado * 1

                            #Se comparan los avances en emision b y 0, para guardar el mayor valor
                            if calculo_real_b > calculo_real_0:
                                avance_documento = calculo_real_b
                                fecha_documento = fecha_emision_b

                            #Se comparan los avances en emision b y 0, para guardar el mayor valor
                            if calculo_real_b < calculo_real_0:
                                avance_documento = calculo_real_0
                                fecha_documento = fecha_emision_0

                            #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
                            if avance_documento != 0:
                                avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
                                valor_documento = 1 
                            cont = cont + 1

                #Si no hay versiones, pasa al siguiente documento
                if not versiones:
                    pass

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
                avance_semanal = calculo_avance_final/largo_fechas
                proyeccion = (diferencia / avance_semanal) - diferencia_arreglo_fecha
                contador = 0

                if  calculo_avance_final < 100 and calculo_avance_final > 0:

                    #Variables
                    avance_inicial_dos = []
                    avance_final_dos = []
                    avance_fechas_controles = []
                    fechas_controles_recorrer = []
                    contador_versiones = 0
                    posterior_fecha = ultima_fecha

                    #Funcion para agregar nuevas fechas
                    while contador < proyeccion:
                        if ultima_fecha < dia_actual and dia_actual < posterior_fecha:
                            fechas_controles.append(dia_actual)
                        ultima_fecha = ultima_fecha + timedelta(days=7)
                        posterior_fecha = ultima_fecha + timedelta(days=7)
                        fechas_controles.append(ultima_fecha)
                        contador = contador + 1

                    #Se recorren las fechas de control para guardar las que necesitan evaluarse
                    for fechas in fechas_controles:
                        if fechas <= dia_actual:
                            fechas_controles_recorrer.append(fechas)
                            avance_fechas_controles.append(0)

                    #Se almacenan los dato del documento
                    for doc in documentos:
                        fecha_emision_0 = doc.fecha_Emision_0
                        fecha_emision_b = doc.fecha_Emision_B
                        versiones = Version.objects.filter(documento_fk=doc).last()
                        cont = 0

                        #Si exite una version
                        if versiones:
                            contador_versiones = contador_versiones + 1
                            fecha_version = versiones.fecha
                            revision_documento = versiones.revision
                            valor_documento = 0

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

                                    #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                    for revision in TYPES_REVISION[5:]:
                                        if revision[0] == revision_documento and fecha_version <= controles:
                                            calculo_real_0 = valor_ganado * 1
                                        if cont == (len(fechas_controles) - 1):
                                            if revision[0] == revision_documento and fecha_version > controles:                                
                                                calculo_real_0 = valor_ganado * 1

                                    #Se comparan los avances en emision b y 0, para guardar el mayor valor
                                    if calculo_real_b > calculo_real_0:
                                        avance_documento = calculo_real_b
                                        fecha_documento = fecha_emision_b

                                    #Se comparan los avances en emision b y 0, para guardar el mayor valor
                                    if calculo_real_b < calculo_real_0:
                                        avance_documento = calculo_real_0
                                        fecha_documento = fecha_emision_0

                                    #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
                                    if avance_documento != 0:
                                        avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
                                        valor_documento = 1 
                                    cont = cont + 1

                        #Si no hay versiones, pasa al siguiente documento
                        if not versiones:
                            pass

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
                    avance_semanal = calculo_avance_final/largo_fechas
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

                    #Se almacena avance real en lista final
                    avance_final = avance_final_dos

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
        lista_avance_real = self.reporte_curva_s_avance_real()
        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        avance_esperado = []
        lista_final_esperado = []
        diferencia = 0
        contador = 0
        numero = 100
        
        if valor_ganado != 0:
            
            #Calculo del avance esperado por fecha de control
            fecha_emision_b = 0
            fecha_emision_0 = 0
            fechas_controles = lista_final[0][0]
            valor_ganado = (100 / valor_ganado)

            diferencia = len(lista_avance_real) - len(fechas_controles)

            for controles in fechas_controles:
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
                avance_esperado = [format(calculo_avanceEsperado, '.2f')]
                lista_final_esperado.append(avance_esperado)

            if diferencia > 0:
                while contador < diferencia:
                    avance_esperado = [format(numero, '.2f')]
                    lista_final_esperado.append(avance_esperado)
                    contador = contador + 1

        if valor_ganado == 0:
            avance_esperado = [int(valor_ganado)]
            lista_final_esperado.append(avance_esperado)

        return lista_final_esperado

    def reporte_curva_s_fechas(self):
        
        lista_final = self.Obtener_fechas()
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        lista_avance_real = self.reporte_curva_s_avance_real()
        fechas_controles = lista_final[0][0]
        diferencia = 0
        contador = 0
        ultima_fecha = 0
        posterior_fecha = 0
        dia_actual = timezone.now()

        if valor_ganado !=0:

            diferencia = len(lista_avance_real) - len(fechas_controles)
            
            if diferencia > 0:
                for fechas in fechas_controles:
                    ultima_fecha = fechas
                
                posterior_fecha = ultima_fecha

                while contador < diferencia:
                    if ultima_fecha < dia_actual and dia_actual < posterior_fecha:
                        fechas_controles.append(dia_actual)
                    ultima_fecha = ultima_fecha + timedelta(days=7)
                    posterior_fecha = ultima_fecha + timedelta(days=7)
                    fechas_controles.append(ultima_fecha)
                    contador = contador + 1 

        if valor_ganado == 0:         
            fechas_controles = ['Sin registros']
            fechas_controles.append(fechas_controles)

        return fechas_controles        

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
        lista_inicial = []
        lista_final = []
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
            espacios = espacios / 10
        else:
            espacios = 1

        return int(espacios)

    def valor_eje_x_grafico_tres(self):

        #Llamado para un método definido anteriormente
        lista_grafico_uno = self.reporte_total_documentos()
        lista_inicial = []
        lista_final = []
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
            espacios = espacios / 10
        else:
            espacios = 1

        return int(espacios)          

    ###################################################
    #                                                 #
    #                                                 #
    #            METODO PARA EXPLAYAR INFO            #
    #                                                 #
    #                                                 #
    ###################################################

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lista_final'] = self.reporte_general()
        context['lista_final_largo'] = len(self.reporte_total_documentos())
        context['lista_final_largo'] = len(self.reporte_general()) 
        context['lista_emisiones'] = self.reporte_emisiones()
        context['lista_emisiones_largo'] = len(self.reporte_emisiones()) 
        context['lista_total_documentos_emitidos'] = self.reporte_total_documentos_emitidos()
        context['lista_total_documentos_emitidos_largo'] = len(self.reporte_total_documentos_emitidos()) 
        context['lista_total_documentos'] = self.reporte_total_documentos()
        context['lista_total_documentos_largo'] = len(self.reporte_total_documentos()) 
        context['lista_curva_s_avance_real'] = self.reporte_curva_s_avance_real()
        context['lista_curva_s_avance_real_largo'] = len(self.reporte_curva_s_avance_real()) 
        context['lista_curva_s_avance_esperado'] = self.reporte_curva_s_avance_esperado()
        context['lista_curva_s_avance_esperado_largo'] = len(self.reporte_curva_s_avance_esperado()) 
        context['lista_curva_s_fechas'] = self.reporte_curva_s_fechas()
        context['lista_curva_s_fechas_largo'] = len(self.reporte_curva_s_fechas()) 
        context['tamano_grafico_uno'] = self.valor_eje_x_grafico_uno()
        context['espacios_grafico_uno'] = self.espacios_eje_x_grafico_uno()
        context['tamano_grafico_tres'] = self.valor_eje_x_grafico_tres()
        context['espacios_grafico_tres'] = self.espacios_eje_x_grafico_tres()

        return context