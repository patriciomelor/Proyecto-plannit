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
from analitica.models import CurvasBase, CurvasBaseHH
from datetime import datetime, time, timedelta
from configuracion.models import HistorialUmbrales

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
        user_roles = [1,2,4,5]
        qs1 = self.get_queryset()
        qs2 = Version.objects.select_related('documento_fk').filter(documento_fk__in=qs1, owner__perfil__rol_usuario__in=user_roles).order_by('fecha') #.select_related("owner").filter(owner__in=users)
        return qs2

    def get_versiones_last(self):
        qs1 = self.get_queryset()
        qs2 = Version.objects.select_related('documento_fk').filter(documento_fk__in=qs1).order_by('fecha') #.select_related("owner").filter(owner__in=users)
        return qs2

        ###################################################
        #                                                 #
        #                                                 #
        #   Variables para tabla                          #
        #                                                 #
        #                                                 #
        ###################################################

    def get_users(self, *args, **kwargs):
        users=[]
        rol = self.request.user.perfil.rol_usuario
        if rol == 1:
            users = self.proyecto.participantes.prefetch_related("perfil").all().filter(perfil__rol_usuario__in=[1,2,3,4,5,6], is_superuser=False, is_active=True).order_by('perfil__empresa')
        elif rol >=2 and rol <=3:
            users = self.proyecto.participantes.prefetch_related("perfil").all().filter(perfil__rol_usuario__in=[1,2,3], is_superuser=False, is_active=True).order_by('perfil__empresa')
        elif rol >= 4 and rol <=6:
            users = self.proyecto.participantes.prefetch_related("perfil").all().filter(perfil__rol_usuario__in=[4,5,6], is_superuser=False, is_active=True).order_by('perfil__empresa')
        else:
            users = None

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
        
        #Llamado curva s porcentual
        reporte_curva_s_avance_real = self.reporte_curva_s_avance_real()
        reporte_curva_s_avance_esperado = self.reporte_curva_s_avance_esperado()
        reporte_curva_s_fechas = self.reporte_curva_s_fechas()

        #Llamado curva s HH
        reporte_curva_s_avance_real_hh = self.reporte_curva_s_avance_real_hh()
        reporte_curva_s_avance_esperado_hh = self.reporte_curva_s_avance_esperado_hh()
        reporte_curva_s_fechas_hh = self.reporte_curva_s_fechas_hh()

        #Llamado tablas
        datos_tabla = self.datos_tabla()

        context['umbrales'] = HistorialUmbrales.objects.filter(proyecto=self.proyecto).order_by('pk')

        #Llamado funciones curva s porcentual
        context['lista_curva_s_avance_real'] = reporte_curva_s_avance_real
        context['lista_curva_s_avance_real_largo'] = len(reporte_curva_s_avance_real) 
        context['lista_curva_s_avance_esperado'] = reporte_curva_s_avance_esperado
        context['lista_curva_s_avance_esperado_largo'] = len(reporte_curva_s_avance_esperado) 
        context['lista_curva_s_fechas'] = reporte_curva_s_fechas
        context['lista_curva_s_fechas_largo'] = len(reporte_curva_s_fechas) 

        #Llamado funciones curva s HH
        context['lista_curva_s_avance_real_hh'] = reporte_curva_s_avance_real_hh
        context['lista_curva_s_avance_real_largo_hh'] = len(reporte_curva_s_avance_real_hh) 
        context['lista_curva_s_avance_esperado_hh'] = reporte_curva_s_avance_esperado_hh
        context['lista_curva_s_avance_esperado_largo_hh'] = len(reporte_curva_s_avance_esperado_hh) 
        context['lista_curva_s_fechas_hh'] = reporte_curva_s_fechas_hh
        context['lista_curva_s_fechas_largo_hh'] = len(reporte_curva_s_fechas_hh) 

        context['usuarios'] = self.get_users()
        context["proyecto"] = self.proyecto

        context['datos_tabla'] = datos_tabla[0]

        context['datos_tabla_emergente'] = datos_tabla[1]

        #Curva base porcentual
        qs = CurvasBase.objects.filter(proyecto=self.proyecto).last()
        context['curvaBase'] = qs

        #Curva base HH
        qs_hh = CurvasBaseHH.objects.filter(proyecto=self.proyecto).last()
        context['curvaBaseHH'] = qs_hh

        return context
       
    def datos_tabla(self):

        lista_inicial = []
        lista_final = []
        lista_ventanas = []
        lista = []
        documentos = self.get_queryset()
        versiones_documentos = self.get_versiones_last()
        total_documentos = len(documentos)
        fechas = self.Obtener_fechas()
        fechas = fechas[0][0]
        semana_actual_dias_revision = timezone.now()
        semana_actual = semana_actual_dias_revision.replace(tzinfo = None)
        fechas_para_documentos = self.reporte_curva_s_fechas()

        #Variables para funciones
        doc_emitidos = []
        doc_aprobados = []
        doc_rev_cliente = []
        doc_rev_contratista = []
        doc_atrasados_b = []
        doc_atrasados_0 = []
        doc_esperados_rev_b = []
        doc_real_rev_b = []
        doc_por_emitir_rev_b = []
        doc_emitidos_rev_b = []
        doc_esperados_rev_0 = []
        doc_real_rev_0 = []
        doc_por_emitir_rev_0 = []
        doc_emitidos_rev_0 = []
        
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
        avance_semanal_programado = 0
        avance_semanal_real = 0

        #Variables documentos esperados y reales
        contador_fechas_semanal = 0
        contador_semanal_b = 0
        contador_semanal_0 = 0
        contador_emitidos_b_sin_0 = 0
        # contador_esperados_b_sin_0 = 0
        contador_emitidos_semana_b = 0
        contador_emitidos_semana_0 = 0

        #Obtener paquetes
        clientes = [1,2,3]        
        contratistas = [4,5,6]        
        cantidad_paquetes_cliente = Paquete.objects.filter(destinatario__perfil__rol_usuario__in=clientes, proyecto=self.proyecto).count()
        cantidad_paquetes_contratista = Paquete.objects.filter(destinatario__perfil__rol_usuario__in=contratistas, proyecto=self.proyecto).count()

        #Funcion para calcular documentos que deberian ser emitidos en una semana
        if fechas_para_documentos:
            for fecha in fechas_para_documentos:
                if str(fecha) <= str(semana_actual):
                    contador_fechas_semanal = contador_fechas_semanal + 1

            fecha_control = fechas_para_documentos[contador_fechas_semanal]
            fecha_anterior = fechas_para_documentos[contador_fechas_semanal - 1]

            for doc in documentos:
                fecha_emision_0 = doc.fecha_Emision_0
                fecha_emision_0 = fecha_emision_0.replace(tzinfo = None)
                fecha_emision_b = doc.fecha_Emision_B
                fecha_emision_b = fecha_emision_b.replace(tzinfo = None)

                if contador_fechas_semanal != 0:

                    if fecha_emision_b >= fecha_anterior and fecha_emision_b <= fecha_control:
                        contador_semanal_b = contador_semanal_b + 1
                        doc_por_emitir_rev_b.append(doc)

                    if fecha_emision_0 >= fecha_anterior and fecha_emision_0 <= fecha_control:
                        contador_semanal_0 = contador_semanal_0 + 1
                        doc_por_emitir_rev_0.append(doc)
                
                if contador_fechas_semanal == 0:

                    if fecha_emision_b <= fecha_control:
                        contador_semanal_b = contador_semanal_b + 1
                        doc_por_emitir_rev_b.append(doc)

                    if fecha_emision_0 <= fecha_control:
                        contador_semanal_0 = contador_semanal_0 + 1
                        doc_por_emitir_rev_0.append(doc)                    

        #Obtener otros datos 
        for doc in documentos:
            comprobacion_first = 0
            version_first = 0
            version_last = 0
            version_rev_0 = 0
            comprobacion_rev_0 = 0
            dias_revision = 0
            fecha_version_paquete = 0

            #Se cuentan los documentos atrasados
            fecha_emision_0 = doc.fecha_Emision_0
            fecha_emision_0 = fecha_emision_0.replace(tzinfo = None)
            fecha_emision_b = doc.fecha_Emision_B
            fecha_emision_b = fecha_emision_b.replace(tzinfo = None)
            
            if semana_actual >= fecha_emision_b:
                contador_b = contador_b + 1
                doc_esperados_rev_b.append(doc)

            if semana_actual >= fecha_emision_0:
                contador_0 = contador_0 + 1
                doc_esperados_rev_0.append(doc)

            #Se recorren las versiones por documento para obtener la primera y ultima
            for versiones in versiones_documentos:
                if comprobacion_rev_0 == 0:
                    if doc == versiones.documento_fk and versiones.revision > 4:
                        version_rev_0 = versiones
                        comprobacion_rev_0 = 1
                if doc == versiones.documento_fk and comprobacion_first == 0:
                    version_first = versiones
                    version_last = versiones
                    comprobacion_first = 1
                if doc == versiones.documento_fk:
                    version_last = versiones

            #calculos respecto al estado cliente
            if version_first != 0:

                #Calculo de días de revision
                paquete = version_last.paquete_set.first()
                paquete_first = version_first.paquete_set.first()
                fecha_paquete_semanal = 0
                if paquete and paquete_first:
                    fecha_paquete_semanal = paquete_first.fecha_creacion
                    fecha_paquete_semanal = fecha_paquete_semanal.replace(tzinfo = None)

                    if version_last.estado_cliente == 5:
                        dias_revision = 0
                    else:
                        fecha_version_paquete = paquete.fecha_creacion
                        dias_revision = abs((semana_actual_dias_revision - fecha_version_paquete).days)

                #Se cuentan las emisiones de documentos en B
                contador_emitidos_b = contador_emitidos_b + 1

                #Calculo del promedio de demora emisión en b
                fecha_version = version_first.fecha
                fecha_version = fecha_version.replace(tzinfo = None)
                diferencia = (fecha_version - fecha_emision_b).days
                prom_demora_emisión_B = prom_demora_emisión_B + diferencia
                contador_demora_b = contador_demora_b + 1

                #Se obtienes las variables necesarias
                # paquete_first = version_first.paquete_set.all()
                fecha_version = version_last.fecha
                fecha_version = fecha_version.replace(tzinfo = None)
                estado_cliente = version_last.estado_cliente
                estado_contratista = version_last.estado_contratista

                #Versiones en revision en b
                if version_last.revision <= 5:
                    doc_emitidos_rev_b.append([doc, version_last, dias_revision, paquete])

                #Versiones en revision en 0
                if version_last.revision > 5:
                    doc_emitidos_rev_b.append([doc, version_first, dias_revision, paquete_first])
                    doc_emitidos_rev_0.append([doc, version_last, dias_revision, paquete])

                #Verisones emitidas en la semana
                if contador_fechas_semanal != 0 and fecha_paquete_semanal != 0:
                    if fecha_paquete_semanal >= fecha_anterior and fecha_paquete_semanal <= fecha_control:
                        if version_first.revision <= 5:
                            contador_emitidos_semana_b = contador_emitidos_semana_b + 1
                            doc_real_rev_b.append([doc, version_first, dias_revision, paquete_first])

                        if version_rev_0:
                            if version_rev_0.revision > 5:
                                paquete_rev_0 = version_rev_0.paquete_set.first()
                                contador_emitidos_semana_0 = contador_emitidos_semana_0 + 1
                                doc_real_rev_0.append([doc, version_rev_0, dias_revision, paquete_rev_0])

                if contador_fechas_semanal == 0 and fecha_paquete_semanal != 0:
                    if fecha_paquete_semanal <= fecha_control:
                        if version_first.revision <= 5:
                            contador_emitidos_semana_b = contador_emitidos_semana_b + 1
                            doc_real_rev_b.append([doc, version_first, dias_revision, paquete_first])

                        if version_rev_0:
                            if version_rev_0.revision > 5:
                                paquete_rev_0 = version_rev_0.paquete_set.first()
                                contador_emitidos_semana_0 = contador_emitidos_semana_0 + 1
                                doc_real_rev_0.append([doc, version_rev_0, dias_revision, paquete_rev_0])

                #Se obtienen y comparan los estados del cliente
                for cliente in ESTADOS_CLIENTE[1:]:
                    if estado_cliente == cliente[0] and estado_cliente != 3 and estado_cliente !=5:
                        documentos_revision_contratista = documentos_revision_contratista + 1
                        doc_rev_contratista.append([doc, version_last, dias_revision, paquete])

                #Se obtienen y comparan los estados del contratista
                for cliente in ESTADO_CONTRATISTA[1:]:
                    if estado_contratista == cliente[0]:
                        documentos_revision_cliente = documentos_revision_cliente + 1
                        doc_rev_cliente.append([doc, version_last, dias_revision, paquete])
                
                #Se realizan calculos para aprobado con comentarios
                #Preguntar a deavys si aprobado con comentarios se encuentra en disposicion del contratista
                if paquete_first:
                    if estado_cliente == 5:
                        fecha_paquete = paquete_first[0].fecha_creacion.replace(tzinfo = None)
                        diferencia = abs((fecha_version - fecha_paquete).days)
                        tiempo_ciclo_aprobación = tiempo_ciclo_aprobación + diferencia
                        documentos_aprobados = documentos_aprobados + 1
                        doc_aprobados.append([doc, version_last, dias_revision, paquete])

                #calculos para revisiones de documentos
                revision = version_last.revision
                for estados in TYPES_REVISION[6:]:
                    if revision == estados[0]:
                        contador_emitidos_0 = contador_emitidos_0 + 1
                        diferencia =(fecha_version - fecha_emision_0).days
                        prom_demora_emisión_0 = prom_demora_emisión_0 + diferencia
                        contador_demora_0 = contador_demora_0 + 1

                #contar versiones emitidas 
                contador_emitidos = contador_emitidos + 1
                doc_emitidos.append([doc, version_last, dias_revision, paquete])

            if version_first == 0:

                #Calculo del promedio de demora emisión en 0
                if semana_actual > fecha_emision_0:
                    diferencia =(semana_actual - fecha_emision_0).days
                    prom_demora_emisión_0 = prom_demora_emisión_0 + diferencia
                    contador_demora_0 = contador_demora_0 + 1
                    doc_atrasados_0.append(doc)
                    documentos_atrasados_0 = documentos_atrasados_0 + 1
                #Calculo del promedio de demora emisión en b
                if semana_actual > fecha_emision_b:
                    diferencia = (semana_actual - fecha_emision_b).days
                    prom_demora_emisión_B = prom_demora_emisión_B + diferencia
                    contador_demora_b = contador_demora_b + 1
                    doc_atrasados_b.append(doc)
                    documentos_atrasados_B = documentos_atrasados_B + 1


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

        esperado_corto = 0
        largo_esperado = 0

        #Calculo de documentos reales emitidos en b
        contador_emitidos_b_sin_0 = contador_emitidos_b
        
        proyecto = self.proyecto
        
        if proyecto.tipo_porcentaje_avance == 0:
            lista_avance_real = self.reporte_curva_s_avance_real()
            avance_esperado = self.reporte_curva_s_avance_esperado()
        
        if proyecto.tipo_porcentaje_avance == 1:
            lista_avance_real = self.reporte_curva_s_avance_real_hh()
            avance_esperado = self.reporte_curva_s_avance_esperado_hh()
        
        #Obtener avance real y esperado
        if lista_avance_real[0][1] != -1:
            if contador_emitidos != 0:
                #Obtener avance real curva s 
                if total_documentos != 0:
                    for avance in lista_avance_real:
                        if avance[1] == 0:
                            avance_real = avance[0]
                            contador_real = contador_real + 1
                    for esperado in avance_esperado:
                        largo_esperado = largo_esperado + 1
                    #Obtener avance esperado curva s
                    if contador_real > largo_esperado: 
                        avance_programado = avance_esperado[-1][0] 
                        esperado_corto = 1
                    else:
                        avance_programado = avance_esperado[contador_real -1][0]

            #Condicional para cuando el avance real posee solo un valor
            if contador_real == 0:
                avance_semanal_real = float(lista_avance_real[contador_real][0]) - float(lista_avance_real[contador_real][0]) 
                avance_semanal_programado = float(avance_esperado[contador_real][0]) - float(avance_esperado[contador_real][0])
                avance_semanal_programado = format(avance_semanal_programado, '.2f')
                avance_semanal_real = format(avance_semanal_real, '.2f')

            #Obtener avance semanal programado y avance semanal real
            if contador_real != 0 and esperado_corto == 0:
                contador_real = contador_real - 1
                avance_semanal_real = float(lista_avance_real[contador_real][0]) - float(lista_avance_real[contador_real - 1][0]) 
                avance_semanal_programado = float(avance_esperado[contador_real][0]) - float(avance_esperado[contador_real - 1][0])
                avance_semanal_programado = format(avance_semanal_programado, '.2f')
                avance_semanal_real = format(avance_semanal_real, '.2f')
                
            if contador_real != 0 and esperado_corto == 1:
                contador_real = contador_real - 1
                avance_semanal_real = float(lista_avance_real[contador_real][0]) - float(lista_avance_real[contador_real - 1][0]) 
                avance_semanal_programado = float(0)
                avance_semanal_programado = format(avance_semanal_programado, '.2f')
                avance_semanal_real = format(avance_semanal_real, '.2f')

        if lista_avance_real[0][1] == -1: 
            avance_real = '0.00'
            contador_fechas = 0
            unico = 1
            semana = 0
            for date in fechas:
                if str(date) >= str(semana_actual) and unico == 1:
                    avance_programado = avance_esperado[contador_fechas][0]
                    semana = contador_fechas
                    unico = 0
                contador_fechas = contador_fechas + 1
            
            if semana != 0:
                avance_semanal_programado = float(avance_esperado[semana][0]) - float(avance_esperado[semana - 1][0])
                avance_semanal_programado = format(avance_semanal_programado, '.2f') 
        
        #Se almacenan los datos obtenidos
        lista_inicial = [total_documentos, contador_emitidos, documentos_aprobados, documentos_atrasados_0, documentos_revision_cliente, documentos_revision_contratista, documentos_atrasados_B, tiempo_ciclo_aprobación, prom_demora_emisión_B, prom_demora_emisión_0, cantidad_paquetes_contratista, cantidad_paquetes_cliente, avance_programado, avance_real, avance_semanal_programado, avance_semanal_real, contador_b, contador_0, contador_emitidos_b_sin_0, contador_emitidos_0, contador_semanal_b, contador_semanal_0, contador_emitidos_semana_b, contador_emitidos_semana_0]
        lista_final.append(lista_inicial)
        lista_ventanas = [doc_emitidos, doc_aprobados, doc_rev_cliente, doc_rev_contratista, doc_atrasados_b, doc_atrasados_0, doc_emitidos_rev_b, doc_emitidos_rev_0, doc_esperados_rev_b, doc_esperados_rev_0, doc_por_emitir_rev_b, doc_por_emitir_rev_0, doc_real_rev_b, doc_real_rev_0]

        lista.append(lista_final)
        lista.append(lista_ventanas)

        return lista

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

        curva_base = CurvasBase.objects.filter(proyecto=self.proyecto).last()
        if valor_ganado !=0:

            if curva_base:

                curva_base = curva_base.datos_lista
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
        rev_letra = self.proyecto.rev_letra
        
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

            if len(fechas_controles_recorrer) == 1:
                fechas_controles_recorrer.append(fechas_controles[1])
                avance_fechas_controles.append(0)

            #Se almacenan los dato del documento
            for doc in documentos:
                cont = 0
                cont2 = 0
                for versiones in versiones_documentos:
                    if str(doc.Codigo_documento) == str(versiones.documento_fk):
                        if versiones.revision > 1 and cont == 0:
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
                    validacion = 1

                    #Se calcula el avance real en la fecha de control que corresponda
                    for controles in fechas_controles_recorrer:
                        if validacion == 1:
                            validacion = 0
                            cont = cont + 1
                            continue

                        if validacion == 0:
                            if valor_documento == 0:
                                calculo_real_0 = 0
                                calculo_real_b = 0
                                avance_documento = 0

                                #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                for revision in TYPES_REVISION[2:5]:
                                    if revision[0] == revision_documento and fecha_version <= controles:
                                        calculo_real_b = valor_ganado * float(rev_letra/100)
                                    if cont == (len(fechas_controles) - 1):
                                        if revision[0] == revision_documento and fecha_version > controles:                              
                                            calculo_real_b = valor_ganado * float(rev_letra/100)

                                if contador_avance == 0:
                                    #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                    for revision in TYPES_REVISION[6:]:
                                        if revision[0] == revision_documento and fecha_version <= controles:
                                            calculo_real_0 = valor_ganado * 1
                                        if cont == (len(fechas_controles) - 1):
                                            if revision[0] == revision_documento and fecha_version > controles:                                
                                                calculo_real_0 = valor_ganado * 1

                                if contador_avance != 0:
                                    #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                    for revision in TYPES_REVISION[6:]:
                                        if revision[0] == revision_documento and fecha_version <= controles:
                                            calculo_real_0 = valor_ganado * float(1.0 - float(rev_letra/100))
                                        if cont == (len(fechas_controles) - 1):
                                            if revision[0] == revision_documento and fecha_version > controles:                                
                                                calculo_real_0 = valor_ganado * float(1.0 - float(rev_letra/100))

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

                        if len(fechas_controles_recorrer) == 1:
                            fechas_controles_recorrer.append(fechas_controles[1])
                            avance_fechas_controles.append(0)

                        #Se recorren las versiones a calcular el avance real
                        for docs in lista_versiones:
                            contador_avance = 0

                            for versiones in docs[1]:
                                contador_versiones = contador_versiones + 1
                                fecha_version = versiones.fecha.replace(tzinfo=None)
                                revision_documento = versiones.revision
                                valor_documento = 0
                                cont = 0
                                validacion = 1

                                #Se calcula el avance real en la fecha de control que corresponda
                                for controles in fechas_controles_recorrer:
                                    if validacion == 1:
                                        validacion = 0
                                        cont = cont + 1
                                        continue

                                    if validacion == 0:
                                        if valor_documento == 0:
                                            calculo_real_0 = 0
                                            calculo_real_b = 0
                                            avance_documento = 0

                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                            for revision in TYPES_REVISION[2:5]:
                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                    calculo_real_b = valor_ganado * float(rev_letra/100)
                                                if cont == (len(fechas_controles) - 1):
                                                    if revision[0] == revision_documento and fecha_version > controles:                              
                                                        calculo_real_b = valor_ganado * float(rev_letra/100)

                                            if contador_avance == 0:
                                                #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                for revision in TYPES_REVISION[6:]:
                                                    if revision[0] == revision_documento and fecha_version <= controles:
                                                        calculo_real_0 = valor_ganado * 1
                                                    if cont == (len(fechas_controles) - 1):
                                                        if revision[0] == revision_documento and fecha_version > controles:                                
                                                            calculo_real_0 = valor_ganado * 1

                                            if contador_avance != 0:
                                                #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                for revision in TYPES_REVISION[6:]:
                                                    if revision[0] == revision_documento and fecha_version <= controles:
                                                        calculo_real_0 = valor_ganado * float(1.0 - float(rev_letra/100))
                                                    if cont == (len(fechas_controles) - 1):
                                                        if revision[0] == revision_documento and fecha_version > controles:                                
                                                            calculo_real_0 = valor_ganado * float(1.0 - float(rev_letra/100))

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
                avance_inicial = [0, -1, 0]
                avance_final.append(avance_inicial)

        #Si no existen documentos, se almacenan valores vacios en el arreglo final
        if valor_ganado == 0:
               avance_inicial = []
               avance_final = []
               avance_inicial = [valor_ganado, -1, 0]
               avance_final.append(avance_inicial)

        return avance_final

    def reporte_curva_s_avance_esperado(self):
                
        lista_final = self.Obtener_fechas()
        documentos = self.get_queryset()
        valor_ganado = len(documentos)
        avance_esperado = []
        lista_final_esperado = []
        rev_letra = self.proyecto.rev_letra

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
                            calculo_avanceEsperado = valor_ganado * float(rev_letra/100) + calculo_avanceEsperado                      
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

    ###################################################
    #                                                 #
    #                                                 #
    #   GRÁFICO DE CURVA S PARA HH                    #
    #                                                 #
    #                                                 #
    ###################################################

    def Obtener_fechas_hh(self):
        elementos_final = []
        documentos = self.get_queryset()
        valor_ganado = len(documentos)
        curva_base = CurvasBaseHH.objects.filter(proyecto=self.proyecto).last()

        if valor_ganado !=0:

            if curva_base:

                curva_base = curva_base.datos_lista

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

    def reporte_curva_s_avance_real_hh(self):

        documentos = self.get_queryset()
        valor_ganado = len(documentos)
        total_hh = 0
        lista_final = self.Obtener_fechas_hh()
        dia_actual = timezone.now()
        dia_actual = dia_actual.replace(tzinfo = None)
        versiones_documentos = self.get_versiones()
        rev_letra = self.proyecto.rev_letra
        
        if valor_ganado !=0:

            #Variables                
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

            if len(fechas_controles_recorrer) == 1:
                fechas_controles_recorrer.append(fechas_controles[1])
                avance_fechas_controles.append(0)

            #Se almacenan los dato del documento
            for doc in documentos:
                cont = 0
                cont2 = 0
                for versiones in versiones_documentos:
                    if str(doc.Codigo_documento) == str(versiones.documento_fk):
                        if versiones.revision > 1 and cont == 0:
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

                #Calculo del total de HH
                total_hh = total_hh + doc.hh_emision_0

            if total_hh != 0:

                #Se recorren las versiones a calcular el avance real
                for docs in lista_versiones:
                    contador_avance = 0
                    hh_doc = docs[0].hh_emision_0

                    for versiones in docs[1]:
                        contador_versiones = contador_versiones + 1
                        fecha_version = versiones.fecha.replace(tzinfo=None)
                        revision_documento = versiones.revision
                        valor_documento = 0
                        cont = 0
                        validacion = 1
                        prueba = versiones.estado_cliente

                        if prueba:

                            if prueba == 3:

                                #Se calcula el avance real en la fecha de control que corresponda
                                for controles in fechas_controles_recorrer:
                                    if validacion == 1:
                                        validacion = 0
                                        cont = cont + 1
                                        continue

                                    if validacion == 0:
                                        if valor_documento == 0:
                                            avance_documento = 0

                                            if contador_avance == 0:
                                                if fecha_version <= controles:
                                                    avance_documento = float((hh_doc * 100)/total_hh)
                                                if cont == (len(fechas_controles) - 1):
                                                    if fecha_version > controles:                                
                                                        avance_documento = float((hh_doc * 100)/total_hh)

                                            if contador_avance != 0:
                                                if fecha_version <= controles:
                                                    avance_documento = float((hh_doc * float(100 - rev_letra))/total_hh)
                                                if cont == (len(fechas_controles) - 1):
                                                    if fecha_version > controles:                                
                                                        avance_documento = float((hh_doc * float(100 - rev_letra))/total_hh)

                                            #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
                                            if avance_documento != 0:
                                                avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
                                                valor_documento = 1 
                                                contador_avance = contador_avance + 1
                                            cont = cont + 1

                            if prueba != 3:

                                #Se calcula el avance real en la fecha de control que corresponda
                                for controles in fechas_controles_recorrer:
                                    if validacion == 1:
                                        validacion = 0
                                        cont = cont + 1
                                        continue

                                    if validacion == 0:
                                        if valor_documento == 0:
                                            calculo_real_0 = 0
                                            calculo_real_b = 0
                                            avance_documento = 0

                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                            for revision in TYPES_REVISION[2:5]:
                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                    calculo_real_b = float((hh_doc * rev_letra)/total_hh)
                                                if cont == (len(fechas_controles) - 1):
                                                    if revision[0] == revision_documento and fecha_version > controles:                              
                                                        calculo_real_b = float((hh_doc * rev_letra)/total_hh)

                                            if contador_avance == 0:
                                                #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                for revision in TYPES_REVISION[6:]:
                                                    if revision[0] == revision_documento and fecha_version <= controles:
                                                        calculo_real_0 = float((hh_doc * 100)/total_hh)
                                                    if cont == (len(fechas_controles) - 1):
                                                        if revision[0] == revision_documento and fecha_version > controles:                                
                                                            calculo_real_0 = float((hh_doc * 100)/total_hh)

                                            if contador_avance != 0:
                                                #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                for revision in TYPES_REVISION[6:]:
                                                    if revision[0] == revision_documento and fecha_version <= controles:
                                                        calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)
                                                    if cont == (len(fechas_controles) - 1):
                                                        if revision[0] == revision_documento and fecha_version > controles:                                
                                                            calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)

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

                        if not prueba:

                            #Se calcula el avance real en la fecha de control que corresponda
                            for controles in fechas_controles_recorrer:
                                if validacion == 1:
                                    validacion = 0
                                    cont = cont + 1
                                    continue

                                if validacion == 0:
                                    if valor_documento == 0:
                                        calculo_real_0 = 0
                                        calculo_real_b = 0
                                        avance_documento = 0

                                        #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                        for revision in TYPES_REVISION[2:5]:
                                            if revision[0] == revision_documento and fecha_version <= controles:
                                                calculo_real_b = float((hh_doc * rev_letra)/total_hh)
                                            if cont == (len(fechas_controles) - 1):
                                                if revision[0] == revision_documento and fecha_version > controles:                              
                                                    calculo_real_b = float((hh_doc * rev_letra)/total_hh)

                                        if contador_avance == 0:
                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                            for revision in TYPES_REVISION[6:]:
                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                    calculo_real_0 = float((hh_doc * 100)/total_hh)
                                                if cont == (len(fechas_controles) - 1):
                                                    if revision[0] == revision_documento and fecha_version > controles:                                
                                                        calculo_real_0 = float((hh_doc * 100)/total_hh)

                                        if contador_avance != 0:
                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                            for revision in TYPES_REVISION[6:]:
                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                    calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)
                                                if cont == (len(fechas_controles) - 1):
                                                    if revision[0] == revision_documento and fecha_version > controles:                                
                                                        calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)

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
                    avance_semanal = calculo_avance_final/largo_fechas

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

                            if len(fechas_controles_recorrer) == 1:
                                fechas_controles_recorrer.append(fechas_controles[1])
                                avance_fechas_controles.append(0)

                            #Se recorren las versiones a calcular el avance real
                            for docs in lista_versiones:
                                contador_avance = 0
                                hh_doc = docs[0].hh_emision_0

                                for versiones in docs[1]:
                                    contador_versiones = contador_versiones + 1
                                    fecha_version = versiones.fecha.replace(tzinfo=None)
                                    revision_documento = versiones.revision
                                    valor_documento = 0
                                    cont = 0
                                    validacion = 1

                                    prueba = versiones.estado_cliente

                                    if prueba:

                                        if prueba == 3:

                                            #Se calcula el avance real en la fecha de control que corresponda
                                            for controles in fechas_controles_recorrer:
                                                if validacion == 1:
                                                    validacion = 0
                                                    cont = cont + 1
                                                    continue

                                                if validacion == 0:
                                                    if valor_documento == 0:
                                                        avance_documento = 0

                                                        if contador_avance == 0:
                                                            if fecha_version <= controles:
                                                                avance_documento = float((hh_doc * 100)/total_hh)
                                                            if cont == (len(fechas_controles) - 1):
                                                                if fecha_version > controles:                                
                                                                    avance_documento = float((hh_doc * 100)/total_hh)

                                                        if contador_avance != 0:
                                                            if fecha_version <= controles:
                                                                avance_documento = float((hh_doc * float(100 - rev_letra))/total_hh)
                                                            if cont == (len(fechas_controles) - 1):
                                                                if fecha_version > controles:                                
                                                                    avance_documento = float((hh_doc * float(100 - rev_letra))/total_hh)

                                                        #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
                                                        if avance_documento != 0:
                                                            avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
                                                            valor_documento = 1 
                                                            contador_avance = contador_avance + 1
                                                        cont = cont + 1

                                        if prueba != 3:

                                            #Se calcula el avance real en la fecha de control que corresponda
                                            for controles in fechas_controles_recorrer:
                                                if validacion == 1:
                                                    validacion = 0
                                                    cont = cont + 1
                                                    continue

                                                if validacion == 0:
                                                    if valor_documento == 0:
                                                        calculo_real_0 = 0
                                                        calculo_real_b = 0
                                                        avance_documento = 0

                                                        #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                        for revision in TYPES_REVISION[2:5]:
                                                            if revision[0] == revision_documento and fecha_version <= controles:
                                                                calculo_real_b = float((hh_doc * rev_letra)/total_hh)
                                                            if cont == (len(fechas_controles) - 1):
                                                                if revision[0] == revision_documento and fecha_version > controles:                              
                                                                    calculo_real_b = float((hh_doc * rev_letra)/total_hh)

                                                        if contador_avance == 0:
                                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                            for revision in TYPES_REVISION[6:]:
                                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                                    calculo_real_0 = float((hh_doc * 100)/total_hh)
                                                                if cont == (len(fechas_controles) - 1):
                                                                    if revision[0] == revision_documento and fecha_version > controles:                                
                                                                        calculo_real_0 = float((hh_doc * 100)/total_hh)

                                                        if contador_avance != 0:
                                                            #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                            for revision in TYPES_REVISION[6:]:
                                                                if revision[0] == revision_documento and fecha_version <= controles:
                                                                    calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)
                                                                if cont == (len(fechas_controles) - 1):
                                                                    if revision[0] == revision_documento and fecha_version > controles:                                
                                                                        calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)

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

                                    if not prueba:

                                        #Se calcula el avance real en la fecha de control que corresponda
                                        for controles in fechas_controles_recorrer:
                                            if validacion == 1:
                                                validacion = 0
                                                cont = cont + 1
                                                continue

                                            if validacion == 0:
                                                if valor_documento == 0:
                                                    calculo_real_0 = 0
                                                    calculo_real_b = 0
                                                    avance_documento = 0

                                                    #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                    for revision in TYPES_REVISION[2:5]:
                                                        if revision[0] == revision_documento and fecha_version <= controles:
                                                            calculo_real_b = float((hh_doc * rev_letra)/total_hh)
                                                        if cont == (len(fechas_controles) - 1):
                                                            if revision[0] == revision_documento and fecha_version > controles:                              
                                                                calculo_real_b = float((hh_doc * rev_letra)/total_hh)

                                                    if contador_avance == 0:
                                                        #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                        for revision in TYPES_REVISION[6:]:
                                                            if revision[0] == revision_documento and fecha_version <= controles:
                                                                calculo_real_0 = float((hh_doc * 100)/total_hh)
                                                            if cont == (len(fechas_controles) - 1):
                                                                if revision[0] == revision_documento and fecha_version > controles:                                
                                                                    calculo_real_0 = float((hh_doc * 100)/total_hh)

                                                    if contador_avance != 0:
                                                        #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
                                                        for revision in TYPES_REVISION[6:]:
                                                            if revision[0] == revision_documento and fecha_version <= controles:
                                                                calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)
                                                            if cont == (len(fechas_controles) - 1):
                                                                if revision[0] == revision_documento and fecha_version > controles:                                
                                                                    calculo_real_0 = float((hh_doc * float(100 - rev_letra))/total_hh)

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

            if total_hh == 0:
                avance_inicial = []
                avance_final = []
                avance_inicial = [total_hh]
                avance_final.append(avance_inicial)


        #Si no existen documentos, se almacenan valores vacios en el arreglo final
        if valor_ganado == 0:
            avance_inicial = []
            avance_final = []
            avance_inicial = [valor_ganado]
            avance_final.append(avance_inicial)

        return avance_final

    def reporte_curva_s_avance_esperado_hh(self):
                
        lista_final = self.Obtener_fechas_hh()
        documentos = self.get_queryset()
        valor_ganado = len(documentos)
        avance_esperado = []
        lista_final_esperado = []
        diferencia = 0
        rev_letra = self.proyecto.rev_letra
        
        if valor_ganado != 0:
            
            #Calculo del avance esperado por fecha de control
            fecha_emision_b = 0
            fecha_emision_0 = 0
            fechas_controles = lista_final[0][0]
            contador_largo = 0
            total_hh = 0

            for doc in documentos:
                total_hh = total_hh + doc.hh_emision_0

            if total_hh != 0:

                for controles in fechas_controles:
                    if contador_largo < len(fechas_controles):
                        calculo_avanceEsperado = 0
                        for doc in documentos:                  
                            fecha_emision_b = doc.fecha_Emision_B.replace(tzinfo=None)
                            fecha_emision_0 = doc.fecha_Emision_0.replace(tzinfo=None)
                            hh_doc = doc.hh_emision_0

                            #Se calcula el avance esperado mediante la comparación de la fecha de control y la fecha de emisión en B - 0
                            if fecha_emision_b <= controles and fecha_emision_0 > controles:
                                calculo_avanceEsperado = float((hh_doc * rev_letra)/total_hh) + calculo_avanceEsperado                      
                            if fecha_emision_0 <= controles and fecha_emision_b < controles:
                                calculo_avanceEsperado = float((hh_doc * 100)/total_hh) + calculo_avanceEsperado

                        #Se almacena el avance esperado hasta la fecha de control
                        avance_esperado = [format(calculo_avanceEsperado, '.2f')]
                        lista_final_esperado.append(avance_esperado)
                    contador_largo = contador_largo + 1
                
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

            if total_hh == 0:
                avance_esperado = [int(total_hh)]
                lista_final_esperado.append(avance_esperado)


        if valor_ganado == 0:
            avance_esperado = [int(valor_ganado)]
            lista_final_esperado.append(avance_esperado)

        return lista_final_esperado

    def reporte_curva_s_fechas_hh(self):
        
        lista_final = self.Obtener_fechas_hh()
        valor_ganado = self.get_queryset().count()
        lista_avance_real = self.reporte_curva_s_avance_real_hh()
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