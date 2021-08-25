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
from analitica.models import CurvasBase
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

class EscritorioView(ProyectoMixin, TemplateView):
    template_name = "administrador/Escritorio/dash.html"

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
        #   Variables para tabla                          #
        #                                                 #
        #                                                 #
        ###################################################

    def get_users(self, *args, **kwargs):
        rol = self.request.user.perfil.rol_usuario
        if rol <=3 and rol >=1:
            users = self.proyecto.participantes.prefetch_related("perfil").all().filter(perfil__rol_usuario__in=[1,2,3])
        if rol <=6 and rol >=4:
            users = self.proyecto.participantes.prefetch_related("perfil").all().filter(perfil__rol_usuario__in=[4,5,6])
            
        return users

    ###################################################
    #                                                 #
    #                                                 #
    #            METODO PARA EXPLAYAR INFO            #
    #                                                 #
    #                                                 #
    ###################################################

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reporte_curva_s_avance_real = self.reporte_curva_s_avance_real()
        reporte_curva_s_avance_esperado = self.reporte_curva_s_avance_esperado()
        reporte_curva_s_fechas = self.reporte_curva_s_fechas()
 
        context['lista_curva_s_avance_real'] = reporte_curva_s_avance_real
        context['lista_curva_s_avance_real_largo'] = len(reporte_curva_s_avance_real) 
        context['lista_curva_s_avance_esperado'] = reporte_curva_s_avance_esperado
        context['lista_curva_s_avance_esperado_largo'] = len(reporte_curva_s_avance_esperado) 
        context['lista_curva_s_fechas'] = reporte_curva_s_fechas
        context['lista_curva_s_fechas_largo'] = len(reporte_curva_s_fechas) 
        context['usuarios'] = self.get_users()
        context["proyecto"] = self.proyecto
        context['datos_tabla'] = self.datos_tabla()

        ## Opción 2
        qs = CurvasBase.objects.filter(proyecto=self.proyecto).last()
        context['curvaBase'] = qs

        return context
       
    def datos_tabla(self):

        lista_inicial = []
        lista_final = []
        documentos = self.get_queryset()
        versiones_documentos = self.get_versiones_last()
        total_documentos = len(documentos)
        lista_avance_real = self.reporte_curva_s_avance_real()
        fechas = self.Obtener_fechas()
        fechas = fechas[0][0]
        avance_esperado = self.reporte_curva_s_avance_esperado()
        semana_actual = timezone.now()
        semana_actual = semana_actual.replace(tzinfo = None)

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
        fecha_emision_0 = 0
        fecha_emision_b = 0
        diferencia = 0
        contador_b = 0
        contador_0 = 0
        contador_emitidos_b = 0
        contador_emitidos_0 = 0

        #Obtener paquetes
        clientes = [1,2,3]        
        contratistas = [4,5,6]        
        cantidad_paquetes_cliente = Paquete.objects.filter(destinatario__perfil__rol_usuario__in=clientes, proyecto=self.proyecto).count()
        cantidad_paquetes_contratista = Paquete.objects.filter(destinatario__perfil__rol_usuario__in=contratistas, proyecto=self.proyecto).count()

        #Obtener otros datos 
        for doc in documentos:
            comprobacion_first = 0
            version_first = 0
            version_last = 0

            #Se cuentan los documentos atrasados
            fecha_emision_0 = doc.fecha_Emision_0
            fecha_emision_0 = fecha_emision_0.replace(tzinfo = None)
            fecha_emision_b = doc.fecha_Emision_B
            fecha_emision_b = fecha_emision_b.replace(tzinfo = None)
            
            if semana_actual >= fecha_emision_b:
                contador_b = contador_b + 1     
            if semana_actual >= fecha_emision_0:
                contador_0 = contador_0 + 1

            #Se recorren las versiones por documento para obtener la primera y ultima
            for versiones in versiones_documentos:
                if str(doc.Codigo_documento) == str(versiones.documento_fk) and comprobacion_first == 0:
                    version_first = versiones
                    comprobacion_first = 1
                if str(doc.Codigo_documento) == str(versiones.documento_fk):
                    version_last = versiones

            #calculos respecto al estado cliente
            if version_first != 0:

                #Se cuentan las emisiones de documentos en B
                contador_emitidos_b = contador_emitidos_b + 1

                #Calculo del promedio de demora emisión en b
                fecha_version = version_first.fecha
                fecha_version = fecha_version.replace(tzinfo = None)
                diferencia = (fecha_version - fecha_emision_b).days
                prom_demora_emisión_B = prom_demora_emisión_B + diferencia
                contador_demora_b = contador_demora_b + 1

                #Se obtienes las variables necesarias
                paquete_first = version_first.paquete_set.all()
                fecha_version = version_last.fecha
                fecha_version = fecha_version.replace(tzinfo = None)
                estado_cliente = version_last.estado_cliente
                estado_contratista = version_last.estado_contratista

                #Se obtienen y comparan los estados del cliente
                for cliente in ESTADOS_CLIENTE[1:]:
                    if estado_cliente == cliente[0] and estado_cliente != 3 and estado_cliente !=5:
                        documentos_revision_contratista = documentos_revision_contratista + 1
                        
                #Se obtienen y comparan los estados del contratista
                for cliente in ESTADO_CONTRATISTA[1:]:
                    if estado_contratista == cliente[0]:
                        documentos_revision_cliente = documentos_revision_cliente + 1
                
                #Se realizan calculos para aprobado con comentarios
                #Preguntar a deavys si aprobado con comentarios se encuentra en disposicion del contratista
                if estado_cliente == 5:
                    fecha_paquete = paquete_first[0].fecha_creacion.replace(tzinfo = None)
                    diferencia = abs((fecha_version - fecha_paquete).days)
                    tiempo_ciclo_aprobación = tiempo_ciclo_aprobación + diferencia
                    documentos_aprobados = documentos_aprobados + 1

                #calculos para revisiones de documentos
                revision = version_last.revision
                for estados in TYPES_REVISION[5:]:
                    if revision == estados[0]:
                        contador_emitidos_0 = contador_emitidos_0 + 1
                        diferencia =(fecha_version - fecha_emision_0).days
                        prom_demora_emisión_0 = prom_demora_emisión_0 + diferencia
                        contador_demora_0 = contador_demora_0 + 1

                #contar versiones emitidas 
                contador_emitidos = contador_emitidos + 1

            if version_first == 0:

                #Calculo del promedio de demora emisión en b
                if semana_actual >= fecha_emision_0:
                    diferencia =(semana_actual - fecha_emision_0).days
                    prom_demora_emisión_0 = prom_demora_emisión_0 + diferencia
                    contador_demora_0 = contador_demora_0 + 1
                if semana_actual >= fecha_emision_b:
                    diferencia = (semana_actual - fecha_emision_b).days
                    prom_demora_emisión_B = prom_demora_emisión_B + diferencia
                    contador_demora_b = contador_demora_b + 1

        #Dar formato a valores de los promedios
        if documentos_aprobados != 0:
            tiempo_ciclo_aprobación = float(tiempo_ciclo_aprobación)/documentos_aprobados
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
            documentos_atrasados_0 = abs(documentos_atrasados_0)

        #Obtener avance real y esperado
        if contador_emitidos != 0:
            #Obtener avance real curva s       
            if total_documentos != 0:
                for avance in lista_avance_real:
                    if avance[1] == 0:
                        avance_real = avance[0]
                        contador_real = contador_real + 1
                contador_real = contador_real - 1
                #Obtener avance esperado curva s 
                avance_programado = avance_esperado[contador_real][0]  

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
            
            if not curva_base:

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
                avance_semanal = calculo_avance_final/(largo_fechas - 1)
                
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
        documentos = self.get_queryset()
        valor_ganado = len(documentos)
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
                contador_largo = contador_largo + 1

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