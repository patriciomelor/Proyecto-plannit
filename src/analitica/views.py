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

        estados_documento = []
        estados_final = []

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        if documentos_totales != 0:
        
            #Obtener lista de las últimas versiones de cada documento
            for doc in documentos: 
                versiones = Version.objects.filter(documento_fk=doc).last()

                if versiones:

                    lista_actual = [versiones, doc] 
                    lista_final.append(lista_actual)

                if not versiones:
                    
                    pass

            #Obtener lista de cantidad de documentos por tipo de versión
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

                        #Comparar que la versión no posea ningón estado de revisión
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
                    
                    for revision in TYPES_REVISION[5:]:
                        
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
    
    def reporte_curva_s_avance_esperado(self):
                
        lista_actual = []
        lista_final = []

        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()
        avance_esperado = []
        lista_final_esperado = []

        if valor_ganado !=0:

            valor_ganado = (100 / valor_ganado)
            documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))

            #Obtener la ultima fecha de emisión en B y en 0
            fecha_emision_b = 0
            fecha_emision_0 = 0
            ultima_fecha_b = 0
            ultima_fecha_0 = 0
            ultima_de_dos = 0
            cont = 0

            for doc in documentos:

                if cont == 0:
                    
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0
                    ultima_fecha_b = fecha_emision_b
                    ultima_fecha_0 = fecha_emision_0
                    cont = 1
                
                if cont != 0:
                    
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0

                    if fecha_emision_b > ultima_fecha_b:

                        ultima_fecha_b = fecha_emision_b

                    if fecha_emision_0 > ultima_fecha_0:
                    
                        ultima_fecha_0 = fecha_emision_0

            #Verificar cuál de las dos fechas, emisión B y 0, es la última
            if ultima_fecha_b >= ultima_fecha_0:

                ultima_de_dos = ultima_fecha_b

            if ultima_fecha_b < ultima_fecha_0:

                ultima_de_dos = ultima_fecha_0

            #Obtener fechas de inicio y termino de proyecto
            fecha_inicio = self.proyecto.fecha_inicio
            fecha_termino = self.proyecto.fecha_termino
            fecha_posterior = self.proyecto.fecha_inicio

            if ultima_de_dos > fecha_termino:

                fecha_termino = ultima_de_dos

            #Se alamacena fecha de inicio del proyecto en la Lista de Controles
            fechas_controles = []
            fechas_controles.append(fecha_inicio)
            fecha_actual = fecha_inicio
            
            #Se almacenan semana a semana hasta curbrir la última fecha de Emisión en 0
            while fecha_actual < fecha_termino and fecha_posterior < fecha_termino:
                
                fecha_actual = fecha_actual + timedelta(days=7)
                fecha_posterior = fecha_actual + timedelta(days=7)
                fechas_controles.append(fecha_actual)
            
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

    def reporte_curva_s_avance_real(self):

        lista_actual = []
        lista_final = []
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        if valor_ganado !=0:

            valor_ganado = (100 / valor_ganado)
            documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
            documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

            #Obtener la ultima fecha de emisión en B y en 0
            fecha_emision_b = 0
            fecha_emision_0 = 0
            ultima_fecha_b = 0
            ultima_fecha_0 = 0
            ultima_de_dos = 0
            cont = 0

            for doc in documentos:

                if cont == 0:
                    
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0
                    ultima_fecha_b = fecha_emision_b
                    ultima_fecha_0 = fecha_emision_0
                    cont = 1
                
                if cont != 0:
                    
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0

                    if fecha_emision_b > ultima_fecha_b:

                        ultima_fecha_b = fecha_emision_b

                    if fecha_emision_0 > ultima_fecha_0:
                    
                        ultima_fecha_0 = fecha_emision_0

            #Verificar cuál de las dos fechas, emisión B y 0, es la última
            if ultima_fecha_b >= ultima_fecha_0:

                ultima_de_dos = ultima_fecha_b

            if ultima_fecha_b < ultima_fecha_0:

                ultima_de_dos = ultima_fecha_0

            #Obtener fechas de inicio y termino de proyecto
            fecha_inicio = self.proyecto.fecha_inicio
            fecha_termino = self.proyecto.fecha_termino
            fecha_posterior = self.proyecto.fecha_inicio

            if ultima_de_dos > fecha_termino:

                fecha_termino = ultima_de_dos

            #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
            fechas_controles = []
            avance_fechas_controles = []
            fechas_controles.append(fecha_inicio)
            avance_fechas_controles.append(0)
            fecha_actual = fecha_inicio
            
            #Se almacenan semana a semana hasta curbrir la fecha de termino del proyecto
            while fecha_actual < fecha_termino and fecha_posterior < fecha_termino:
                
                fecha_actual = fecha_actual + timedelta(days=7)
                fecha_posterior = fecha_actual + timedelta(days=7)
                fechas_controles.append(fecha_actual)

                #Se rellena el arreglo que aumentará el avance real por documento
                avance_fechas_controles.append(0)

            fechas_controles.append(fecha_termino)
            avance_fechas_controles.append(0)
            
            #Calculo del avance real por fecha de control
            avance_inicial = []
            avance_final = []
            #documentos_atrasados = []
            fecha_version = 0
            fecha_documento = 0

            semana_actual = timezone.now()

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

                        #Se realiza la comparación hasta que la fecha de control contenga el día actual
                        if semana_actual >= controles and valor_documento == 0:

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
                            #if avance_documento != 0 and fecha_documento > fecha_version:
                            if avance_documento != 0:

                                avance_fechas_controles[cont] = int(avance_fechas_controles[cont] + avance_documento)
                                valor_documento = 1

                            # #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida posteriormente a la emision estipulada
                            # if avance_documento != 0 and fecha_documento <= fecha_version:

                            #     avance_fechas_controles[cont] = int(avance_fechas_controles[cont] + avance_documento)
                            #     documentos_atrasados.append(doc.Especialidad)
                            #     valor_documento = 1
                            
                            #Aumenta el contador para almacenar en la fecha de control correspondiente  
                            #print("Revision: ", versiones.revision, " Especialidad: ", doc.Especialidad, " Fecha control: ", cont, " Avance documento: ", avance_documento)
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
                    avance_inicial = [calculo_avance_final]
                    avance_final.append(avance_inicial)
                    contador_final = contador_final + 1                                   

        #Si no existen documentos, se almacenan valores vacios en el arreglo final
        if valor_ganado == 0:
                
               avance_inicial = []
               avance_final = []

               avance_inicial = [valor_ganado]
               avance_final.append(avance_inicial)

        return avance_final

    def reporte_curva_s_fechas(self):
        
        lista_actual = []
        lista_final = []
        valor_ganado = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))        
        
        if valor_ganado != 0:

            #Obtener la ultima fecha de emisión en B y en 0
            fecha_emision_b = 0
            fecha_emision_0 = 0
            ultima_fecha_b = 0
            ultima_fecha_0 = 0
            ultima_de_dos = 0
            cont = 0

            for doc in documentos:

                if cont == 0:
                    
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0
                    ultima_fecha_b = fecha_emision_b
                    ultima_fecha_0 = fecha_emision_0
                    cont = 1
                
                if cont != 0:
                    
                    fecha_emision_b = doc.fecha_Emision_B
                    fecha_emision_0 = doc.fecha_Emision_0

                    if fecha_emision_b > ultima_fecha_b:

                        ultima_fecha_b = fecha_emision_b

                    if fecha_emision_0 > ultima_fecha_0:
                    
                        ultima_fecha_0 = fecha_emision_0

            #Verificar cuál de las dos fechas, emisión B y 0, es la última
            if ultima_fecha_b >= ultima_fecha_0:

                ultima_de_dos = ultima_fecha_b

            if ultima_fecha_b < ultima_fecha_0:

                ultima_de_dos = ultima_fecha_0

            #Obtener fechas de inicio y termino de proyecto
            fecha_inicio = self.proyecto.fecha_inicio
            fecha_termino = self.proyecto.fecha_termino
            fecha_posterior = self.proyecto.fecha_inicio

            if ultima_de_dos > fecha_termino:

                fecha_termino = ultima_de_dos

            #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
            fechas_controles = []
            fechas_controles.append(fecha_inicio)
            fecha_actual = fecha_inicio
            
            #Se almacenan semana a semana hasta curbrir la última fecha de Emisión en 0
            while fecha_actual < fecha_termino and fecha_posterior < fecha_termino:
                
                fecha_actual = fecha_actual + timedelta(days=7)
                fecha_posterior = fecha_actual + timedelta(days=7)
                fechas_controles.append(fecha_actual)
            
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
        #   OBTENER DOCUMENTOS ATRASADOS                  #
        #                                                 #
        #                                                 #
        ###################################################

    def documentos_atrasados(self):

        lista_atrasados = []
        fecha_version = 0
        fecha_emision_b = 0
        fecha_emision_0 = 0
        revision_documento = 0

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        documentos_totales = Documento.objects.filter(proyecto=self.request.session.get('proyecto')).count()

        if documentos_totales != 0:

            for doc in documentos:

                fecha_emision_b = doc.fecha_Emision_B
                fecha_emision_0 = doc.fecha_Emision_0
                versiones = Version.objects.filter(documento_fk=doc).last()

                if versiones:

                    fecha_version = versiones.fecha
                    revision_documento = versiones.revision

                    for revision in TYPES_REVISION[1:4]:

                        if revision_documento == revision[0]:

                            if fecha_emision_b > fecha_version:

                                lista_final.append(doc)

                    for revision in TYPES_REVISION[5:]:

                        if revision_documento == revision[0]:

                            if fecha_emision_0 > fecha_version:

                                lista_atrasados.append(doc.Codigo_documento)

                if not versiones:

                    pass

        if documentos_totales == 0:

            lista_atrasados.append(0)

        print(lista_atrasados)
        return lista_atrasados                  

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