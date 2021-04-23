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

from datetime import datetime, timedelta



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
        
        #Variables
        lista_atrasados_final = []
        lista_emitidos_final = []
        avance_real = 0
        lista_datos_final = []
        porcentaje = 0
        porcentaje_atrasado = 0
        diferencia = 0        
        #################################################################     

        #Obtener documentos sin emisiones por especialidad
        for especialidad in especialidad_list:
            lista_atrasados = []
            lista_datos_inicial = []
            contador_total = 0
            for doc in lista_final:
                if especialidad == doc[0].Especialidad:
                    lista_atrasados.append(doc[0])
                    contador_total = contador_total + 1
            if contador_total != 0:
                lista_atrasados_final.append([lista_atrasados, contador_total])

        print(lista_atrasados_final)
        #################################################################   

        #Obtener documentos con emisiones por especialidad        
        for especialidad in especialidad_list:
            lista_emitidos = []
            lista_datos_inicial = []
            contador_no_emitidos = 0
            for doc in lista_final_emitidos:
                if especialidad == doc[0].Especialidad:
                    lista_emitidos.append(doc[0])
                    contador_no_emitidos = contador_no_emitidos + 1
            if contador_no_emitidos != 0:
                lista_emitidos_final.append([lista_emitidos, contador_no_emitidos])

        #################################################################   

        #Obtener documentos emitidos vs documentos atrasados
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
            porcentaje = (diferencia/contador_total)*100
            porcentaje = format(porcentaje, '.1f')
            porcentaje_atrasado = float(100) - float(porcentaje)
            diferencia = contador_total - contador_no_emitidos
            lista_datos_inicial = [especialidad, contador_total, contador_no_emitidos, porcentaje, diferencia]
            lista_datos_final.append(lista_datos_inicial)
        ########################################################################################

        #Escritorio solicitado por deavys
        documentos_contador = self.get_queryset().count()
        

        ########################################################################################

        context['Porcentaje'] = format(porcentaje_documentos_emitidos, '.2f')
        context['Porcentaje_atrasado'] = format(porcentaje_atrasado, '.2f')
        context['Cantidad'] = cantidad_documentos
        context['Emitidos'] = cantidad_versiones
        context['Atrasados'] = contador_atrasados
        context['Listado_no_emitidos'] = lista_final
        context['Comparacion'] = lista_datos_final
        context['Listado_emitidos'] = lista_emitidos_final
        context['Listado_final_emitidos'] = lista_final_emitidos

        return context

        ###################################################
        #                                                 #
        #                                                 #
        #   CUARTO GRÁFICO DE CURVA S                     #
        #                                                 #
        #                                                 #
        ###################################################

    def Obtener_fechas(self):

        documentos = self.get_queryset()
        valor_ganado = self.get_queryset().count()

        if valor_ganado !=0:

            valor_ganado = (100 / valor_ganado)
            documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
            documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
            fecha_inicio = self.proyecto.fecha_inicio
            fecha_termino = self.proyecto.fecha_termino
            fecha_posterior = self.proyecto.fecha_inicio

            #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
            fechas_controles = []
            fechas_controles.append(fecha_inicio)
            fecha_actual = fecha_inicio
            
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

            if ultima_de_dos > fecha_termino:
                fecha_termino = ultima_de_dos

            #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
            avance_fechas_controles = []
            avance_fechas_controles.append(0)
            avance_fechas_controles.append(0)
            fecha_actual = primera_de_dos
            
            #Se almacenan semana a semana hasta curbrir la fecha de termino del proyecto
            while fecha_actual < fecha_termino and fecha_posterior < fecha_termino:
                fecha_actual = fecha_actual + timedelta(days=7)
                fecha_posterior = fecha_actual + timedelta(days=7)
                fechas_controles.append(fecha_actual)

                #Se rellena el arreglo que aumentará el avance real por documento
                avance_fechas_controles.append(0)
            
            fechas_controles.append(fecha_termino)
            avance_fechas_controles.append(0)
            elementos = []
            elementos_final = []
            elementos = [fechas_controles, avance_fechas_controles]
            elementos_final.append(elementos)
        
        return elementos_final

    def reporte_curva_s_avance_real(self):

        documentos = self.get_queryset()
        valor_ganado = self.get_queryset().count()
        lista_final = self.Obtener_fechas()

        if valor_ganado !=0:

            valor_ganado = (100 / valor_ganado)
            documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
            documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()                      
            avance_inicial = []
            avance_final = []
            fecha_version = 0
            fecha_documento = 0
            fechas_controles = lista_final[0][0]
            avance_fechas_controles = lista_final[0][1]

            #Se almacenan los dato del documento
            for doc in documentos:
                fecha_emision_0 = doc.fecha_Emision_0
                fecha_emision_b = doc.fecha_Emision_B
                versiones = Version.objects.filter(documento_fk=doc).last()

                #Si exite una version
                if versiones:
                    fecha_version = versiones.fecha
                    revision_documento = versiones.revision
                    cont = 0
                    valor_documento = 0

                    #Se calcula el avance real en la fecha de control que corresponda
                    for controles in fechas_controles:
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

            calculo_avance_final = 0

            #Se calcula el avance real por fecha de control, mediante las sumatorias de estas, cubriendo las fechas de controles hasta el día actual
            contador_final = 0
            for avance in avance_fechas_controles: 
                if contador_final < cont:
                    calculo_avance_final = calculo_avance_final + avance
                    avance_inicial = [format(calculo_avance_final, '.2f')]
                    avance_final.append(avance_inicial)
                    contador_final = contador_final + 1   

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
        calculo_avance_final = float(0)
        contador = 0
        documentos = self.get_queryset()
        valor_ganado = self.get_queryset().count()
        avance_esperado = []
        lista_final_esperado = []

        if valor_ganado !=0:
            
            #Fechas para la proyección de avance real
            for avance in lista_avance_real:
                if contador == (len(lista_avance_real) - 1):
                    calculo_avance_final = float(avance[0])
                contador = contador + 1 
            if calculo_avance_final != 100:
                avance_real_now = 100 - calculo_avance_final
                avance_semanal = calculo_avance_final / float(contador)
                avance_proyeccion = int(avance_real_now / avance_semanal)

            valor_ganado = (100 / valor_ganado)
            documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
            fecha_inicio = self.proyecto.fecha_inicio
            fecha_termino = self.proyecto.fecha_termino
            fecha_posterior = self.proyecto.fecha_inicio
            fechas_controles = lista_final[0][0]

            #Fechas extra para la proyección
            contador_proyeccion = 0
            diferencia = len(fechas_controles) - contador
            avance_proyeccion = avance_proyeccion - diferencia

            if avance_proyeccion <= 10:
                while contador_proyeccion < avance_proyeccion:
                    fecha_termino = fecha_termino + timedelta(days=7)
                    fechas_controles.append(fecha_termino)
                    contador_proyeccion = contador_proyeccion + 1
            else:
                if avance_proyeccion % 2 == 0:
                    avance_proyeccion = avance_proyeccion / 2
                    while contador_proyeccion < avance_proyeccion:
                        fecha_termino = fecha_termino + timedelta(days=14)
                        fechas_controles.append(fecha_termino)
                        contador_proyeccion = contador_proyeccion + 1
                else:
                    avance_proyeccion = (avance_proyeccion - 1 ) / 2
                    while contador_proyeccion < avance_proyeccion:
                        fecha_termino = fecha_termino + timedelta(days=14)
                        fechas_controles.append(fecha_termino)
                        contador_proyeccion = contador_proyeccion + 1
                    fecha_termino = fecha_termino + timedelta(days=7)
                    fechas_controles.append(fecha_termino)
            #Calculo del avance esperado por fecha de control
            fecha_emision_b = 0
            fecha_emision_0 = 0

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

        else:
            avance_esperado = [int(valor_ganado)]
            lista_final_esperado.append(avance_esperado)

        return lista_final_esperado

    def reporte_curva_s_fechas(self):
        
        lista_final = self.Obtener_fechas()
        documentos = self.get_queryset()
        valor_ganado = self.get_queryset().count()
        lista_avance_real = self.reporte_curva_s_avance_real()
        calculo_avance_final = float(0)
        contador = 0       
        
        if valor_ganado != 0:

            #Fechas para la proyección de avance real
            for avance in lista_avance_real:
                if contador == (len(lista_avance_real) - 1):          
                    calculo_avance_final = float(avance[0])
                contador = contador + 1

            if calculo_avance_final != 100:
                avance_real_now = 100 - calculo_avance_final
                avance_semanal = calculo_avance_final / float(contador)
                avance_proyeccion = int(avance_real_now / avance_semanal)

            fecha_inicio = self.proyecto.fecha_inicio
            fecha_termino = self.proyecto.fecha_termino
            fecha_posterior = self.proyecto.fecha_inicio
            fechas_controles = lista_final[0][0]
            semana_actual = timezone.now()

            #Fechas extra para la proyección
            contador_proyeccion = 0
            diferencia = len(fechas_controles) - contador
            avance_proyeccion = avance_proyeccion - diferencia

            if avance_proyeccion <= 10:
                while contador_proyeccion < avance_proyeccion:
                    fecha_termino = fecha_termino + timedelta(days=7)
                    fechas_controles.append(fecha_termino)
                    contador_proyeccion = contador_proyeccion + 1

            else:
                if avance_proyeccion % 2 == 0:
                    avance_proyeccion = avance_proyeccion / 2
                    while contador_proyeccion < avance_proyeccion:
                        fecha_termino = fecha_termino + timedelta(days=14)
                        fechas_controles.append(fecha_termino)
                        contador_proyeccion = contador_proyeccion + 1
                else:
                    avance_proyeccion = (avance_proyeccion - 1 ) / 2
                    while contador_proyeccion < avance_proyeccion:
                        fecha_termino = fecha_termino + timedelta(days=14)
                        fechas_controles.append(fecha_termino)
                        contador_proyeccion = contador_proyeccion + 1
                    fecha_termino = fecha_termino + timedelta(days=7)
                    fechas_controles.append(fecha_termino)
        else:
                
            fechas_controles = []
            fechas_controles.append('Sin registros')

        return fechas_controles

    ###################################################
    #                                                 #
    #                                                 #
    #   OBTENER VALORES DE LOS EJES                   #
    #                                                 #
    #                                                 #
    ###################################################

    def proyeccion(self):

        avance_inicial = []
        avance_final = []
        lista_avance_real = self.reporte_curva_s_avance_real()
        calculo_avance_final = float(0)
        cont = 0
        contador = 0

        #Fechas para la proyección de avance real
        for avance in lista_avance_real:
            if cont == (len(lista_avance_real) - 1):  
                calculo_avance_final = float(avance[0])
            cont = cont + 1

        if calculo_avance_final != 100:           
            avance_real_now = 100 - calculo_avance_final
            avance_semanal = calculo_avance_final / float(cont)
                
            if avance_semanal != 0:           
                avance_proyeccion = int(avance_real_now / avance_semanal)
                if avance_proyeccion <= 10:
                    while contador < avance_proyeccion:                            
                        if contador == (avance_proyeccion - 1):
                            calculo_avance_final = calculo_avance_final + avance_semanal
                            if calculo_avance_final != float(100):                                
                                diferencia = float(100) - calculo_avance_final
                                calculo_avance_final = calculo_avance_final + diferencia
                                avance_inicial = [format(calculo_avance_final, '.2f')]
                                avance_final.append(avance_inicial)  
                                contador = contador + 1 
                            else: 
                                avance_inicial = [format(calculo_avance_final, '.2f')]
                                avance_final.append(avance_inicial)  
                                contador = contador + 1                       
                        else: 
                            calculo_avance_final = calculo_avance_final + avance_semanal
                            avance_inicial = [format(calculo_avance_final, '.2f')]
                            avance_final.append(avance_inicial)  
                            contador = contador + 1
                else:
                    if avance_proyeccion % 2 == 0:
                        avance_proyeccion = avance_proyeccion / 2
                        avance_semanal = avance_semanal * 2
                        while contador < avance_proyeccion:
                            if contador == (avance_proyeccion - 1):
                                calculo_avance_final = calculo_avance_final + avance_semanal
                                if calculo_avance_final != float(100):                                    
                                    diferencia = float(100) - calculo_avance_final
                                    calculo_avance_final = calculo_avance_final + diferencia
                                    avance_inicial = [format(calculo_avance_final, '.2f')]
                                    avance_final.append(avance_inicial)  
                                    contador = contador + 1 
                                else: 
                                    avance_inicial = [format(calculo_avance_final, '.2f')]
                                    avance_final.append(avance_inicial)  
                                    contador = contador + 1                           
                            else:
                                calculo_avance_final = calculo_avance_final + avance_semanal
                                avance_inicial = [format(calculo_avance_final, '.2f')]
                                avance_final.append(avance_inicial)  
                                contador = contador + 1
                    else:
                        avance_proyeccion = ((avance_proyeccion - 1) / 2) + 1
                        avance_semanal = avance_semanal * 2
                        while contador < avance_proyeccion:
                            if contador == (avance_proyeccion - 1):
                                calculo_avance_final = calculo_avance_final + (avance_semanal/2)
                                if calculo_avance_final != float(100):                             
                                    diferencia = float(100) - calculo_avance_final
                                    calculo_avance_final = calculo_avance_final + diferencia
                                    avance_inicial = [format(calculo_avance_final, '.2f')]
                                    avance_final.append(avance_inicial)  
                                    contador = contador + 1 
                                else: 
                                    avance_inicial = [format(calculo_avance_final, '.2f')]
                                    avance_final.append(avance_inicial)  
                                    contador = contador + 1                
                            else:
                                calculo_avance_final = calculo_avance_final + avance_semanal
                                avance_inicial = [format(calculo_avance_final, '.2f')]
                                avance_final.append(avance_inicial)  
                                contador = contador + 1
            else: 
                pass
        
        return avance_final         

    ###################################################
    #                                                 #
    #                                                 #
    #            METODO PARA EXPLAYAR INFO            #
    #                                                 #
    #                                                 #
    ###################################################

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
 
        context['lista_curva_s_avance_real'] = self.reporte_curva_s_avance_real()
        context['lista_curva_s_avance_real_largo'] = len(self.reporte_curva_s_avance_real()) 
        context['lista_curva_s_avance_esperado'] = self.reporte_curva_s_avance_esperado()
        context['lista_curva_s_avance_esperado_largo'] = len(self.reporte_curva_s_avance_esperado()) 
        context['lista_curva_s_fechas'] = self.reporte_curva_s_fechas()
        context['lista_curva_s_fechas_largo'] = len(self.reporte_curva_s_fechas()) 
        context['proyeccion'] = self.proyeccion()
        context['proyeccion_largo'] = len(self.proyeccion()) 

        return context

