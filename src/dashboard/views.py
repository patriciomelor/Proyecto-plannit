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
from panel_carga.choices import TYPES_REVISION, ESTADOS_CLIENTE, ESTADO_CONTRATISTA
import math

from datetime import datetime, time, timedelta



# Create your views here.

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

class WelcomeView(ProyectoMixin, TemplateView):
    template_name = 'administrador/Escritorio/welcome.html'

class RootView(RedirectView):
    pattern_name = 'account_login'

class IndexView(ProyectoMixin, TemplateView):
    template_name = "index-base.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proyecto"] = self.proyecto
        return context
    
# Ejemplo de función
# def diferencia_fechas(fecha_uno, fecha_dos):
    
#     diferencia = 0
#     diferencia = abs((fecha_uno - fecha_dos).days)

#     return diferencia

class EscritorioView(ProyectoMixin, TemplateView):
    template_name = "administrador/Escritorio/dash.html"

    def get_queryset(self):
        listado_versiones_doc = DocFilter(self.request.GET, queryset=Documento.objects.filter(proyecto=self.proyecto))
        return listado_versiones_doc.qs.order_by('Codigo_documento')

        ###################################################
        #                                                 #
        #                                                 #
        #   Variables para tabla                          #
        #                                                 #
        #                                                 #
        ###################################################
        
    def datos_tabla(self):

        lista_inicial = []
        lista_final = []
        documentos = self.get_queryset()
        documentos_contador = self.get_queryset().count()
        total_documentos = self.get_queryset().count()
        lista_avance_real = self.reporte_curva_s_avance_real()
        fechas = self.Obtener_fechas()
        fechas = fechas[0][0]
        avance_esperado = self.reporte_curva_s_avance_esperado()
        semana_actual = timezone.now()

        # print(lista_avance_real)
        # print(avance_esperado)

        #Variables para funciones
        contador_emitidos = 0
        documentos_aprobados = 0
        documentos_atrasados_B = 0
        documentos_atrasados_0 = 0
        documentos_revision_cliente = 0
        documentos_revision_contratista = 0
        tiempo_ciclo_aprobación = 0
        prom_demora_emisión_B = 0
        prom_demora_emisión_0 = 0
        contador_demora_b = 0
        contador_demora_0 = 0
        cantidad_paquetes_cliente = 0
        cantidad_paquetes_contratista = 0
        avance_programado = 0
        avance_real = 0
        contador_real = 0
        contador_esperado = 0
        fecha_emision_0 = 0
        fecha_emision_b = 0
        diferencia = 0
        contador_b = 0
        contador_0 = 0
        contador_emitidos_b = 0
        contador_emitidos_0 = 0
        contador_aprobacion = 0
        verificador_emision_0 = 1 

        #Obtener paquetes
        clientes = [1,2,3]        
        contratistas = [4,5,6]        
        cantidad_paquetes_cliente = Paquete.objects.filter(destinatario__perfil__rol_usuario__in=clientes, proyecto=self.proyecto).count()
        cantidad_paquetes_contratista = Paquete.objects.filter(destinatario__perfil__rol_usuario__in=contratistas, proyecto=self.proyecto).count()

        #Obtener otros datos 
        for doc in documentos:
            versiones = Version.objects.filter(documento_fk=doc).last()
            total_versiones = Version.objects.filter(documento_fk=doc)
            version_first = Version.objects.filter(documento_fk=doc).first()
            fecha_emision_0 = doc.fecha_Emision_0
            fecha_emision_b = doc.fecha_Emision_B
            if semana_actual >= fecha_emision_b:
                contador_b = contador_b + 1     
            if semana_actual >= fecha_emision_0:
                contador_0 = contador_0 + 1
            if versiones:
                contador_emitidos_b = contador_emitidos_b + 1
                paquete_first = version_first.paquete_set.all()
                fecha_version = versiones.fecha
                estado_cliente = versiones.estado_cliente
                estado_contratista = versiones.estado_contratista
                for cliente in ESTADOS_CLIENTE[1:]:
                    if estado_cliente == 5 and cliente[0] == 5:
                        contador_emitidos_0 = contador_emitidos_0 + 1
                        diferencia = abs((fecha_version - paquete_first[0].fecha_creacion).days)
                        tiempo_ciclo_aprobación = tiempo_ciclo_aprobación + diferencia
                        contador_aprobacion = contador_aprobacion + 1
                        documentos_aprobados = documentos_aprobados + 1
                        verificador_emision_0 = 0
                    if estado_cliente == 1 and cliente[0] == 1:
                        documentos_revision_contratista = documentos_revision_contratista + 1
                    if estado_cliente == 2 and cliente[0] == 2:
                        documentos_revision_contratista = documentos_revision_contratista + 1
                    if estado_cliente == 4 and cliente[0] == 4:
                        documentos_revision_contratista = documentos_revision_contratista + 1
                    if estado_cliente == 6 and cliente[0] == 6:
                        contador_emitidos_0 = contador_emitidos_0 + 1
                        documentos_revision_contratista = documentos_revision_contratista + 1
                    if estado_cliente == 7 and cliente[0] == 7:
                        contador_emitidos_0 = contador_emitidos_0 + 1
                        verificador_emision_0 = 0
                    if estado_cliente == 8 and cliente[0] == 8:
                        contador_emitidos_0 = contador_emitidos_0 + 1   
                        verificador_emision_0 = 0                 
                    if estado_cliente == 9 and cliente[0] == 9:
                        contador_emitidos_0 = contador_emitidos_0 + 1 
                        verificador_emision_0 = 0                   
                    if estado_cliente == 10 and cliente[0] == 10:
                        contador_emitidos_0 = contador_emitidos_0 + 1
                        verificador_emision_0 = 0
                if verificador_emision_0 == 1:
                    diferencia =(fecha_version - fecha_emision_0).days
                    prom_demora_emisión_0 = prom_demora_emisión_0 + diferencia
                    contador_demora_0 = contador_demora_0 + 1
                for cliente in ESTADO_CONTRATISTA[1:]:
                    if estado_contratista == 1 and cliente[0] == 1:
                        documentos_revision_cliente = documentos_revision_cliente + 1
                    if estado_contratista == 2 and cliente[0] == 2:
                        documentos_revision_cliente = documentos_revision_cliente + 1
                contador_emitidos = contador_emitidos + 1
            if not versiones:
                #Calculo del promedio de demora emisión en b
                if semana_actual >= fecha_emision_0:
                    diferencia =(semana_actual - fecha_emision_0).days
                    prom_demora_emisión_0 = prom_demora_emisión_0 + diferencia
                    contador_demora_0 = contador_demora_0 + 1
                if semana_actual >= fecha_emision_b:
                    diferencia = (semana_actual - fecha_emision_b).days
                    prom_demora_emisión_B = prom_demora_emisión_B + diferencia
                    contador_demora_b = contador_demora_b + 1
            if total_versiones:
                repeticion = 1
                for ver in total_versiones:
                    fecha_version = ver.fecha
                    estado = ver.revision
                    if estado == 5 and repeticion == 1:
                        diferencia = (fecha_version - fecha_emision_0).days
                        prom_demora_emisión_0 = prom_demora_emisión_0 + diferencia
                        contador_demora_0 = contador_demora_0 + 1
                        repeticion = 0
            if version_first:   
                #Calculo del promedio de demora emisión en b
                fecha_version = version_first.fecha
                diferencia = (fecha_version - fecha_emision_b).days
                prom_demora_emisión_B = prom_demora_emisión_B + diferencia
                contador_demora_b = contador_demora_b + 1

        #Dar formato a valores de los promedios
        if contador_aprobacion != 0:
            tiempo_ciclo_aprobación = float(tiempo_ciclo_aprobación)/contador_aprobacion
            tiempo_ciclo_aprobación = format(float(tiempo_ciclo_aprobación), '.1f')
        if contador_demora_b != 0:
            prom_demora_emisión_B = float(prom_demora_emisión_B)/contador_demora_b
            prom_demora_emisión_B = format(float(prom_demora_emisión_B), '.1f')
        if contador_demora_0 != 0:
            prom_demora_emisión_0 = float(prom_demora_emisión_0)/contador_demora_0
            prom_demora_emisión_0 = format(float(prom_demora_emisión_0), '.1f')

        #Promedio negativos se transforman en 0
        if float(tiempo_ciclo_aprobación) < 0.0:
            tiempo_ciclo_aprobación = 0.0
        if float(prom_demora_emisión_B) < 0.0:
            prom_demora_emisión_B = 0.0
        if float(prom_demora_emisión_0) < 0.0:
            prom_demora_emisión_0 = 0.0
        
        #Calculo de documentos atrasados
        documentos_atrasados_B = contador_b - contador_emitidos_b
        documentos_atrasados_0 = contador_0 - contador_emitidos_0

        if documentos_atrasados_B < 0:
            documentos_atrasados_B = 0
        if documentos_atrasados_0 < 0:
            documentos_atrasados_0 = 0

        #Obtener avance real y esperado
        if contador_emitidos != 0:
            #Obtener avance real curva s       
            if documentos_contador != 0:
                for avance in lista_avance_real:
                    if avance[1] == 0:
                        avance_real = avance[0]
                        contador_real = contador_real + 1
                contador_real = contador_real - 1
                #Obtener avance esperado curva s 
                avance_programado = avance_esperado[contador_real][0]  
                # for esperado in avance_esperado:
                #     if (contador_real - 1) == contador_esperado:
                #         avance_programado = esperado[0]
                #     contador_esperado = contador_esperado + 1

        #Avance real y esperado en caso no existir documentos emitidos
        if contador_emitidos == 0:
            avance_real = '0.0'
            contador_fechas = 0
            # puesto_esperado = 0
            unico = 1
            for date in fechas:
                if date >= semana_actual and unico == 1:
                    # puesto_esperado = contador_fechas
                    avance_programado = avance_esperado[contador_fechas][0]
                    unico = 0
                contador_fechas = contador_fechas + 1
            # avance_programado = avance_esperado[puesto_esperado][0]

        #Obtener avance semanal programado y avance semanal real
        avance_semanal_real = float(lista_avance_real[contador_real][0]) - float(lista_avance_real[contador_real - 1][0]) 
        avance_semanal_programado = float(avance_esperado[contador_real][0]) - float(avance_esperado[contador_real - 1][0])
        avance_semanal_programado = [format(avance_semanal_programado, '.2f')]
        avance_semanal_real = [format(avance_semanal_real, '.2f')]

        print(lista_avance_real[contador_real][0], avance_esperado[contador_real][0], lista_avance_real[contador_real - 1][0], avance_esperado[contador_real - 1][0])
        
        #Se almacenan los datos obtenidos
        lista_inicial = [total_documentos, contador_emitidos, documentos_aprobados, documentos_atrasados_0, documentos_revision_cliente,  documentos_revision_contratista,  documentos_atrasados_B, tiempo_ciclo_aprobación, prom_demora_emisión_B, prom_demora_emisión_0,cantidad_paquetes_contratista, cantidad_paquetes_cliente,  avance_programado, avance_real, avance_semanal_programado[0], avance_semanal_real[0]]
        lista_final.append(lista_inicial)

        return lista_inicial

        ###################################################
        #                                                 #
        #                                                 #
        #   CUARTO GRÁFICO DE CURVA S                     #
        #                                                 #
        #                                                 #
        ###################################################

    def Obtener_fechas(self):
        elementos_final = []
        documentos = self.get_queryset()
        valor_ganado = self.get_queryset().count()
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
            primera_de_dos = primera_de_dos + timedelta(hours=23)
            primera_de_dos = primera_de_dos + timedelta(minutes=59)
            primera_de_dos = primera_de_dos + timedelta(seconds=59)
            primera_de_dos = primera_de_dos + timedelta(microseconds=59)
            primera_de_dos = primera_de_dos + timedelta(milliseconds=59)
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
        valor_ganado = self.get_queryset().count()
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
            contador_fechas = 1

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
                        posterior_fecha = ultima_fecha
                        contador_fechas = 1

                        #Funcion para agregar nuevas fechas
                        while contador < proyeccion:
                            ultima_fecha = ultima_fecha + timedelta(days=7)
                            posterior_fecha = ultima_fecha + timedelta(days=7)
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
        documentos = self.get_queryset()
        valor_ganado = self.get_queryset().count()
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
        valor_ganado = self.get_queryset().count()
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
    #            METODO PARA EXPLAYAR INFO            #
    #                                                 #
    #                                                 #
    ###################################################

    def get_users(self, *args, **kwargs):
        users = self.proyecto.participantes.all()
        return users


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
 
        context['lista_curva_s_avance_real'] = self.reporte_curva_s_avance_real()
        context['lista_curva_s_avance_real_largo'] = len(self.reporte_curva_s_avance_real()) 
        context['lista_curva_s_avance_esperado'] = self.reporte_curva_s_avance_esperado()
        context['lista_curva_s_avance_esperado_largo'] = len(self.reporte_curva_s_avance_esperado()) 
        context['lista_curva_s_fechas'] = self.reporte_curva_s_fechas()
        context['lista_curva_s_fechas_largo'] = len(self.reporte_curva_s_fechas()) 
        context['usuarios'] = self.get_users()
        context["proyecto"] = self.proyecto
        context['datos_tabla'] = self.datos_tabla()

        return context