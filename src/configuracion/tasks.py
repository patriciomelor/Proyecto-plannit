from __future__ import absolute_import, unicode_literals

from django.db import connection
from bandeja_es.models import Version
from os import name

from dmp.celery import app
from notifications.emails import send_email
from notifications.models import Notificacion
from panel_carga.models import Documento, Proyecto
from configuracion.models import Umbral, HistorialUmbrales, NotificacionHU
from panel_carga.choices import TYPES_REVISION, ESTADOS_CLIENTE, ESTADO_CONTRATISTA
from datetime import date, datetime, time, timedelta
from analitica.models import CurvasBase
from django.utils import timezone
import math

# @app.task(name="desviacion")
# def umbral_1(umbral, doc):
#     pass

def users_notifier(proyecto, cliente=None, contratista=None):
    recipients = []
    notification_list = []
    if cliente == True:
        participantes = proyecto.participantes.select_related("perfil").all().filter(perfil__rol_usuario__in = [1,2])
    if contratista == True:
        participantes = proyecto.participantes.select_related("perfil").all().filter(perfil__rol_usuario__in = [4,5])

    for user in participantes:
        recipients.append(user.email)
        notification_list.append(user)

    return [recipients, notification_list]

@app.task(name="umbral_2")
def umbral_2():
    proyectos = Proyecto.objects.all()
    fecha_actual = timezone.now()
    for proyecto in proyectos:
        document_list = []
        revision_list = []
        last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=2).last()
        delta_proyect = (fecha_actual - last_hu.last_checked)


        if delta_proyect.days >= last_hu.cliente_tiempo_control:
            print("Se notifica para proyecto {}!".format(proyecto.nombre))
            documentos = Documento.objects.filter(proyecto=proyecto)
            for documento in documentos:
                revision = Version.objects.filter(documento_fk=documento).last()
                if revision is not None:
                    if revision.estado_cliente == None:
                        delta_rev = (fecha_actual - revision.fecha)
                        if delta_rev.days > last_hu.cliente_variable_atraso:
                            revision_list.append(revision)
                            document_list.append(documento)
                    else:
                        pass
            
            if len(revision_list) != 0:
                usuarios = users_notifier(proyecto=proyecto, cliente=True)
                try:
                    subject = "[UMBRAL {proyecto}] Listado de Revisiones Atrasadas Cliente - {date}".format(proyecto=proyecto.codigo, date=timezone.now().strftime("%d-%B-%y"))
                    send_email(
                        html= 'configuracion/umbral_2.html',
                        context= {
                            "documentos": document_list,
                            "proyecto": proyecto,
                            "atraso": delta_rev.days,
                        },
                        subject=subject,
                        recipients= usuarios[0]
                    )
                    for usuario in usuarios[1]:
                        noti = Notificacion(
                            proyecto=proyecto,
                            usuario=usuario,
                            notification_type=1,
                            text_preview=subject
                        )
                        noti.save()

                        noti_hu = NotificacionHU(
                            h_umbral=last_hu,
                            notificacion=noti,
                        )
                        noti_hu.save()
                        noti_hu.documentos.set(document_list, clear=True)

                    last_hu.last_checked = timezone.now()
                    last_hu.save()
                    
                except Exception as err:
                    error = "Un error Ocurrido al momento de notificar para el Umbral 2. {}".format(err)
                    return error
            else:
                pass
        else:
            pass

    return document_list

@app.task(name="umbral_3")
def umbral_3():
    proyectos = Proyecto.objects.all()
    fecha_actual = timezone.now()
    for proyecto in proyectos:
        revision_list = []
        document_list = []
        last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=3).last()
        delta_proyect = (fecha_actual - last_hu.last_checked)

        if delta_proyect.days >= last_hu.contratista_tiempo_control:
            print("Se notifica para proyecto {}!".format(proyecto.nombre))
            documentos = Documento.objects.filter(proyecto=proyecto)
            for documento in documentos:
                revision = Version.objects.filter(documento_fk=documento).last()
                if revision is not None:
                    if revision.estado_contratista == None:
                        delta_rev = (fecha_actual - revision.fecha)
                        if delta_rev.days >= last_hu.contratista_variable_atraso:
                            revision_list.append(revision)
                            document_list.append(documento)
                    else:
                        pass
             
            subject = "[UMBRAL {proyecto}] Listado de Revisiones Atrasadas Contratistas - {date}".format(proyecto=proyecto.codigo, date=timezone.now().strftime("%d-%B-%y"))
            usuarios = users_notifier(proyecto=proyecto, contratista=True)

            if len(revision_list) != 0:
                try:
                    send_email(
                        html= 'configuracion/umbral_3.html',
                        context= {
                            "revisiones": revision_list,
                            "proyecto": proyecto,
                            "atraso": delta_rev.days,
                        },
                        subject=subject,
                        recipients= usuarios[0]
                    )
                    for usuario in usuarios[1]:
                        noti = Notificacion(
                            proyecto=proyecto,
                            usuario=usuario,
                            notification_type=1,
                            text_preview=subject
                        )
                        noti.save()

                        noti_hu = NotificacionHU(
                            h_umbral=last_hu,
                            notificacion=noti,
                        )
                        noti_hu.save()
                        noti_hu.documentos.set(document_list, clear=True)
                        noti_hu.versiones.set(revision_list, clear=True)

                    last_hu.last_checked = timezone.now()
                    last_hu.save()

                except Exception as err:
                    error = "Un error Ocurrido al momento de notificar para el Umbral 3. {}".format(err)
                    return error
            else:
                pass 
        else:
            pass

    return revision_list

# def get_users_dash(proyecto):
#     users = proyecto.participantes.prefetch_related("perfil").all()
#     lista_usuarios = []

#     for usuarios in users:
#         if usuarios.perfil.rol_usuario == 4 or usuarios.perfil.rol_usuario == 5:
#             lista_usuarios.append(usuarios)             

#     return lista_usuarios

# def Obtener_fechas():
#     elementos_final = []
#     elementos = []
#     conjunto_finales = []
#     proyectos = Proyecto.objects.all()

#     for proyecto in proyectos:
#         documentos = Documento.objects.filter(proyecto=proyecto)        
#         valor_ganado = Documento.objects.filter(proyecto=proyecto).count()

#         if valor_ganado !=0:

#             valor_ganado = (100 / valor_ganado)

#             #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
#             fechas_controles = []
            
#             #Obtener la ultima fecha de emisión en B y en 0
#             fecha_emision_b = 0
#             fecha_emision_0 = 0
#             ultima_fecha_b = 0
#             ultima_fecha_0 = 0
#             ultima_de_dos = 0
#             cont = 0

#             #Obtener la primera fecha por documento
#             primera_fecha_b = 0
#             primera_fecha_0 = 0
#             primera_de_dos = 0

#             for doc in documentos:
#                 if cont == 0:               
#                     fecha_emision_b = doc.fecha_Emision_B
#                     fecha_emision_0 = doc.fecha_Emision_0
#                     ultima_fecha_b = fecha_emision_b
#                     ultima_fecha_0 = fecha_emision_0
#                     primera_fecha_b = doc.fecha_Emision_B
#                     primera_fecha_0 = doc.fecha_Emision_0
#                     cont = 1
                
#                 if cont != 0:   
#                     fecha_emision_b = doc.fecha_Emision_B
#                     fecha_emision_0 = doc.fecha_Emision_0
#                     if fecha_emision_b > ultima_fecha_b:
#                         ultima_fecha_b = fecha_emision_b
#                     if fecha_emision_0 > ultima_fecha_0:                 
#                         ultima_fecha_0 = fecha_emision_0
#                     if fecha_emision_b < primera_fecha_b:               
#                         primera_fecha_b = fecha_emision_b
#                     if fecha_emision_0 < primera_fecha_0:            
#                         primera_fecha_0 = fecha_emision_0

#             #Verificar cuál de las dos fechas, emisión B y 0, es la última
#             if ultima_fecha_b >= ultima_fecha_0:
#                 ultima_de_dos = ultima_fecha_b
#             if ultima_fecha_b < ultima_fecha_0:
#                 ultima_de_dos = ultima_fecha_0
#             if primera_fecha_b < primera_fecha_0:
#                 primera_de_dos = primera_fecha_b
#             if primera_fecha_b > primera_fecha_0:
#                 primera_de_dos = primera_fecha_0

#             #Agregar una semana antes a la primera de los documentos
#             fechas_controles = []
#             primera_de_dos = primera_de_dos + timedelta(hours=23)
#             primera_de_dos = primera_de_dos + timedelta(minutes=59)
#             primera_de_dos = primera_de_dos + timedelta(seconds=59)
#             primera_de_dos = primera_de_dos + timedelta(microseconds=59)
#             primera_de_dos = primera_de_dos + timedelta(milliseconds=59)
#             primera_de_dos = primera_de_dos - timedelta(days=7)
#             fechas_controles.append(primera_de_dos)
#             primera_de_dos = primera_de_dos + timedelta(days=7)
#             fechas_controles.append(primera_de_dos)

#             #Se alamacena la primera fecha de Emisión en B en la Lista de Controles
#             fecha_actual = primera_de_dos
#             fecha_posterior = fecha_actual + timedelta(days=7)
            
#             #Se almacenan semana a semana hasta curbrir la fecha de termino del proyecto
#             while fecha_actual < ultima_de_dos and fecha_posterior < ultima_de_dos:
#                 fecha_actual = fecha_actual + timedelta(days=7)
#                 fecha_posterior = fecha_actual + timedelta(days=7)
#                 fechas_controles.append(fecha_actual)
#             fechas_controles.append(ultima_de_dos)

#             #Se almacena arreglo de fechas en la lista final
#             elementos = [fechas_controles]
#             elementos_final.append(elementos)

#         else:
#             #Se almacena arreglo de fechas en la lista final
#             elementos_final.append([])
        
#         conjunto_finales.append(elementos_final)
    
#     return conjunto_finales

# def reporte_curva_s_avance_real():

#     proyectos = Proyecto.objects.all()
#     lista_final = Obtener_fechas()
#     dia_actual = timezone.now()
#     contador_fechas_grupo = 0
#     conjunto_finales = []

#     for proyecto in proyectos:
#         documentos = Documento.objects.filter(proyecto=proyecto)        
#         valor_ganado = Documento.objects.filter(proyecto=proyecto).count()
#         usuarios = get_users_dash(proyecto=proyecto)
    
#         if valor_ganado !=0:

#             #Variables
#             valor_ganado = (100 / valor_ganado)                     
#             avance_inicial = []
#             avance_final = []
#             fecha_version = 0
#             fechas_controles = lista_final[contador_fechas_grupo][0][0]
#             avance_fechas_controles = []
#             contador_versiones = 0
#             fechas_controles_recorrer = []
#             ultima_fecha = 0
#             contador_fechas = 1
#             lista_versiones = []

#             #Variables final
#             largo_inicial_fechas = len(fechas_controles)
#             largo_necesitado = 0

#             #Se recorren las fechas de control para guardar las que necesitan evaluarse
#             for fechas in fechas_controles:
#                 if fechas <= dia_actual:
#                     fechas_controles_recorrer.append(fechas)
#                     avance_fechas_controles.append(0)
#                 else:
#                     if fechas > dia_actual and contador_fechas == 1:
#                         fechas_controles_recorrer.append(fechas)
#                         avance_fechas_controles.append(0)
#                         contador_fechas = 0
#                 ultima_fecha = fechas

#             #Se almacenan los dato del documento
#             for doc in documentos:
#                 version = Version.objects.filter(documento_fk=doc)
#                 contador = 0
#                 if version:
#                     cont = 0
#                     cont2 = 0

#                     for versiones in version:
#                         for users in usuarios:
#                             nombre = users.first_name + ' ' + users.last_name
#                             if versiones.revision < 5:
#                                 if str(nombre) == str(versiones.owner) and cont == 0:               
#                                     version_letras = versiones
#                                     cont = 1
#                             if versiones.revision > 4:
#                                 if str(nombre) == str(versiones.owner) and cont2 == 0:               
#                                     version_numerica = versiones
#                                     cont2 = 1

#                     if cont == 1 and cont2 == 1:
#                         lista_versiones.append([doc, [version_letras, version_numerica]])

#                     if cont == 1 and cont2 == 0:
#                         lista_versiones.append([doc, [version_letras]])

#                     if cont == 0 and cont2 == 1:
#                         lista_versiones.append([doc, [version_numerica]])

#                 if not version:
#                     pass
#             #Se recorren las versiones a calcular el avance real
#             for docs in lista_versiones:
#                 contador_avance = 0

#                 for versiones in docs[1]:
#                     contador_versiones = contador_versiones + 1
#                     fecha_version = versiones.fecha
#                     revision_documento = versiones.revision
#                     valor_documento = 0
#                     cont = 0

#                     #Se calcula el avance real en la fecha de control que corresponda
#                     for controles in fechas_controles_recorrer:
#                         if valor_documento == 0:
#                             calculo_real_0 = 0
#                             calculo_real_b = 0
#                             avance_documento = 0

#                             #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
#                             for revision in TYPES_REVISION[1:4]:
#                                 if revision[0] == revision_documento and fecha_version <= controles:
#                                     calculo_real_b = valor_ganado * 0.7
#                                 if cont == (len(fechas_controles) - 1):
#                                     if revision[0] == revision_documento and fecha_version > controles:                              
#                                         calculo_real_b = valor_ganado * 0.7

#                             if contador_avance == 0:
#                                 #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
#                                 for revision in TYPES_REVISION[5:]:
#                                     if revision[0] == revision_documento and fecha_version <= controles:
#                                         calculo_real_0 = valor_ganado * 1
#                                     if cont == (len(fechas_controles) - 1):
#                                         if revision[0] == revision_documento and fecha_version > controles:                                
#                                             calculo_real_0 = valor_ganado * 1

#                             if contador_avance != 0:
#                                 #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
#                                 for revision in TYPES_REVISION[5:]:
#                                     if revision[0] == revision_documento and fecha_version <= controles:
#                                         calculo_real_0 = valor_ganado * 0.3
#                                     if cont == (len(fechas_controles) - 1):
#                                         if revision[0] == revision_documento and fecha_version > controles:                                
#                                             calculo_real_0 = valor_ganado * 0.3

#                             #Se comparan los avances en emision b y 0, para guardar el mayor valor
#                             if calculo_real_b > calculo_real_0:
#                                 avance_documento = calculo_real_b                               

#                             #Se comparan los avances en emision b y 0, para guardar el mayor valor
#                             if calculo_real_b < calculo_real_0:
#                                 avance_documento = calculo_real_0

#                             #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
#                             if avance_documento != 0:
#                                 avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
#                                 valor_documento = 1 
#                                 contador_avance = contador_avance + 1
#                             cont = cont + 1

#                 #Si no hay versiones, pasa al siguiente documento
#                 if not versiones:
#                     pass

#             if contador_versiones != 0:
#                 #Se calcula el avance real por fecha de control, mediante las sumatorias de estas, cubriendo las fechas de controles hasta el día actual
#                 contador_final = 0
#                 calculo_avance_final = 0
#                 largo_fechas = len(avance_fechas_controles)
                
#                 for avance in avance_fechas_controles: 
#                     if contador_final < largo_fechas:
#                         calculo_avance_final = calculo_avance_final + avance
#                         avance_inicial = [format(calculo_avance_final, '.2f'), 0]
#                         avance_final.append(avance_inicial)
#                         contador_final = contador_final + 1

#                 #Funcion en caso de que el avance real no sea el 100%
#                 diferencia_arreglo_fecha = len(fechas_controles) - largo_fechas
#                 diferencia = 100 - calculo_avance_final
#                 avance_semanal = calculo_avance_final/(largo_fechas - 1)
                
#                 if avance_semanal != 0:
#                     proyeccion = (diferencia / avance_semanal) - diferencia_arreglo_fecha
#                     contador = 0

#                     if  calculo_avance_final < 100 and calculo_avance_final > 0:

#                         #Variables
#                         avance_inicial_dos = []
#                         avance_final_dos = []
#                         avance_fechas_controles = []
#                         fechas_controles_recorrer = []
#                         contador_versiones = 0
#                         posterior_fecha = ultima_fecha
#                         contador_fechas = 1

#                         #Funcion para agregar nuevas fechas
#                         while contador < proyeccion:
#                             ultima_fecha = ultima_fecha + timedelta(days=7)
#                             posterior_fecha = ultima_fecha + timedelta(days=7)
#                             fechas_controles.append(ultima_fecha)
#                             contador = contador + 1

#                         #Se recorren las fechas de control para guardar las que necesitan evaluarse
#                         for fechas in fechas_controles:
#                             if fechas <= dia_actual:
#                                 fechas_controles_recorrer.append(fechas)
#                                 avance_fechas_controles.append(0)
#                             else:
#                                 if fechas > dia_actual and contador_fechas == 1:
#                                     fechas_controles_recorrer.append(fechas)
#                                     avance_fechas_controles.append(0)
#                                     contador_fechas = 0

#                         #Se recorren las versiones a calcular el avance real
#                         for docs in lista_versiones:
#                             contador_avance = 0

#                             for versiones in docs[1]:
#                                 contador_versiones = contador_versiones + 1
#                                 fecha_version = versiones.fecha
#                                 revision_documento = versiones.revision
#                                 valor_documento = 0
#                                 cont = 0

#                                 #Se calcula el avance real en la fecha de control que corresponda
#                                 for controles in fechas_controles_recorrer:
#                                     if valor_documento == 0:
#                                         calculo_real_0 = 0
#                                         calculo_real_b = 0
#                                         avance_documento = 0

#                                         #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
#                                         for revision in TYPES_REVISION[1:4]:
#                                             if revision[0] == revision_documento and fecha_version <= controles:
#                                                 calculo_real_b = valor_ganado * 0.7
#                                             if cont == (len(fechas_controles) - 1):
#                                                 if revision[0] == revision_documento and fecha_version > controles:                              
#                                                     calculo_real_b = valor_ganado * 0.7

#                                         if contador_avance == 0:
#                                             #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
#                                             for revision in TYPES_REVISION[5:]:
#                                                 if revision[0] == revision_documento and fecha_version <= controles:
#                                                     calculo_real_0 = valor_ganado * 1
#                                                 if cont == (len(fechas_controles) - 1):
#                                                     if revision[0] == revision_documento and fecha_version > controles:                                
#                                                         calculo_real_0 = valor_ganado * 1

#                                         if contador_avance != 0:
#                                             #Se recorren los tipos de version para obtener la del documento actual y realizar el calculo
#                                             for revision in TYPES_REVISION[5:]:
#                                                 if revision[0] == revision_documento and fecha_version <= controles:
#                                                     calculo_real_0 = valor_ganado * 0.3
#                                                 if cont == (len(fechas_controles) - 1):
#                                                     if revision[0] == revision_documento and fecha_version > controles:                                
#                                                         calculo_real_0 = valor_ganado * 0.3

#                                         #Se comparan los avances en emision b y 0, para guardar el mayor valor
#                                         if calculo_real_b > calculo_real_0:
#                                             avance_documento = calculo_real_b                               

#                                         #Se comparan los avances en emision b y 0, para guardar el mayor valor
#                                         if calculo_real_b < calculo_real_0:
#                                             avance_documento = calculo_real_0

#                                         #Se almacena el avance real en la fecha de control estimada, cuando la version fue emitida antes de la emision estipulada
#                                         if avance_documento != 0:
#                                             avance_fechas_controles[cont] = avance_fechas_controles[cont] + avance_documento
#                                             valor_documento = 1 
#                                             contador_avance = contador_avance + 1
#                                         cont = cont + 1

#                             #Si no hay versiones, pasa al siguiente documento
#                             if not versiones:
#                                 pass

#                         #Se calcula el avance real por fecha de control, mediante las sumatorias de estas, cubriendo las fechas de controles hasta el día actual
#                         contador_final = 0
#                         calculo_avance_final = 0
#                         largo_fechas = len(avance_fechas_controles)
                        
#                         for avance in avance_fechas_controles: 
#                             if contador_final < largo_fechas:
#                                 calculo_avance_final = calculo_avance_final + avance
#                                 avance_inicial_dos = [format(calculo_avance_final, '.2f'), 0]
#                                 avance_final_dos.append(avance_inicial_dos)
#                                 contador_final = contador_final + 1

#                         #Funcion en caso de que el avance real no sea el 100%
#                         diferencia_arreglo_fecha = len(fechas_controles) - largo_fechas
#                         diferencia = 100 - calculo_avance_final
#                         avance_semanal = calculo_avance_final/(largo_fechas - 1)
#                         proyeccion = (diferencia / avance_semanal)
#                         contador = 0

#                         proyeccion = math.ceil(proyeccion)
#                         if  calculo_avance_final < 100 and calculo_avance_final > 0:
#                             while contador < proyeccion:
#                                 if contador == (proyeccion - 1):
#                                     calculo_avance_final = 100
#                                     avance_inicial_dos = [format(calculo_avance_final, '.2f'), 1]
#                                     avance_final_dos.append(avance_inicial_dos)
#                                     contador = contador + 1

#                                 else:
#                                     calculo_avance_final = calculo_avance_final + avance_semanal
#                                     avance_inicial_dos = [format(calculo_avance_final, '.2f'), 1]
#                                     avance_final_dos.append(avance_inicial_dos)
#                                     contador = contador + 1                                                                                    

#                         #Se almacena avance real en lista final
#                         avance_final = avance_final_dos

#                         #Calcular extension de fechas
#                         largo_necesitado = largo_fechas + proyeccion
#                         largo_necesitado = largo_necesitado - largo_inicial_fechas

#             if contador_versiones == 0:
#                 avance_inicial = [0]
#                 avance_final.append(avance_inicial)

#         #Si no existen documentos, se almacenan valores vacios en el arreglo final
#         if valor_ganado == 0:
#                 avance_inicial = []
#                 avance_final = []
#                 avance_inicial = [valor_ganado]
#                 avance_final.append(avance_inicial)
        
#         contador_fechas = contador_fechas + 1
#         conjunto_finales.append(avance_final)

#     return conjunto_finales

# def reporte_curva_s_avance_esperado():
                
#     lista_final = Obtener_fechas()
#     lista_avance_real = reporte_curva_s_avance_real()
#     avance_esperado = []
#     lista_final_esperado = []
#     diferencia = 0
#     contador = 0
#     numero = 100
#     contador_fechas = 0
#     conjunto_finales = []

#     proyectos = Proyecto.objects.all()
#     for proyecto in proyectos:
#         documentos = Documento.objects.filter(proyecto=proyecto)        
#         valor_ganado = Documento.objects.filter(proyecto=proyecto).count()
    
#         if valor_ganado != 0:
            
#             #Calculo del avance esperado por fecha de control
#             fecha_emision_b = 0
#             fecha_emision_0 = 0
#             fechas_controles = lista_final[contador_fechas][0][0]
#             valor_ganado = (100 / valor_ganado)

#             diferencia = len(lista_avance_real[contador_fechas]) - len(fechas_controles)

#             for controles in fechas_controles:
#                 calculo_avanceEsperado = 0
#                 for doc in documentos:                  
#                     fecha_emision_b = doc.fecha_Emision_B
#                     fecha_emision_0 = doc.fecha_Emision_0

#                     #Se calcula el avance esperado mediante la comparación de la fecha de control y la fecha de emisión en B - 0
#                     if fecha_emision_b <= controles and fecha_emision_0 > controles:
#                         calculo_avanceEsperado = valor_ganado * 0.7 + calculo_avanceEsperado                      
#                     if fecha_emision_0 <= controles and fecha_emision_b < controles:
#                         calculo_avanceEsperado = valor_ganado * 1 + calculo_avanceEsperado

#                 #Se almacena el avance esperado hasta la fecha de control
#                 avance_esperado = [format(calculo_avanceEsperado, '.2f')]
#                 lista_final_esperado.append(avance_esperado)

#             if diferencia > 0:
#                 while contador < diferencia:
#                     avance_esperado = [format(numero, '.2f')]
#                     lista_final_esperado.append(avance_esperado)
#                     contador = contador + 1

#         if valor_ganado == 0:
#             avance_esperado = [int(valor_ganado)]
#             lista_final_esperado.append(avance_esperado)

#         contador_fechas = contador_fechas + 1
#         conjunto_finales.append(lista_final_esperado)

#     return conjunto_finales

def get_queryset():
    proyectos = Proyecto.objects.all()
    final_list = []
    for proyecto in proyectos:
        qs1 = Documento.objects.filter(proyecto=proyecto)
        final_list.append(qs1)

    return final_list
 
def get_versiones():
    user_roles = [4,5]
    qs1 = get_queryset()
    final_list = []
    for documento in qs1:
        qs2 = Version.objects.select_related('documento_fk').filter(documento_fk__in=documento, owner__perfil__rol_usuario__in=user_roles) #.select_related("owner").filter(owner__in=users)
        final_list.append(qs2)

    return final_list

def Obtener_fechas():
    documentos = get_queryset()
    proyectos = Proyecto.objects.all()
    conjunto_finales = []
    contador_proyecto = 0

    for proyecto in proyectos:
        elementos_final = []
        valor_ganado = len(documentos[contador_proyecto])
        curva_base = CurvasBase.objects.filter(proyecto=proyecto).last().datos_lista

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

                for doc in documentos[contador_proyecto]:
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

                for doc in documentos[contador_proyecto]:
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
        
        conjunto_finales.append(elementos_final)
        contador_proyecto = contador_proyecto + 1
    
    return conjunto_finales

def reporte_curva_s_avance_real():

    documentos_totales = get_queryset()
    contador_fechas_grupo = 0
    conjunto_finales = []
    lista_final = Obtener_fechas()
    dia_actual = timezone.now()
    dia_actual = dia_actual.replace(tzinfo = None)
    versiones_documentos = get_versiones()

    for documentos in documentos_totales:
        valor_ganado = len(documentos)
    
        if valor_ganado !=0:

            #Variables
            valor_ganado = (100 / valor_ganado)                  
            avance_inicial = []
            avance_final = []
            fecha_version = 0
            fechas_controles = lista_final[contador_fechas_grupo][0][0]
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
                for versiones in versiones_documentos[contador_fechas_grupo]:
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
        
        conjunto_finales.append(avance_final)
        contador_fechas_grupo = contador_fechas_grupo + 1

    return conjunto_finales

def reporte_curva_s_avance_esperado():
            
    lista_final = Obtener_fechas()
    documentos_totales = get_queryset()
    contador_fechas_grupo = 0
    conjunto_finales = []
    
    for documentos in documentos_totales:
        valor_ganado = len(documentos)
        diferencia = 0
        avance_esperado = []
        lista_final_esperado = []

        if valor_ganado != 0:
            
            #Calculo del avance esperado por fecha de control
            fecha_emision_b = 0
            fecha_emision_0 = 0
            fechas_controles = lista_final[contador_fechas_grupo][0][0]
            valor_ganado = (100 / valor_ganado)
            contador_largo = 0

            for controles in fechas_controles:
                if contador_largo < (len(fechas_controles)-1):
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

        conjunto_finales.append(lista_final_esperado)

    return conjunto_finales

@app.task(name="umbral_4")
def umbral_4():
    avance_esperado_all = reporte_curva_s_avance_esperado()
    lista_avance_real_all = reporte_curva_s_avance_real()
    avance_programado = 0
    avance_real = 0
    lista_proyectos_atrasados = []
    contador_proyecto = 0
    fecha_actual = timezone.now()
    proyectos = Proyecto.objects.all()

    for proyecto in proyectos:  
        valor_ganado = Documento.objects.filter(proyecto=proyecto).count()
        contador_real = 0
        if valor_ganado != 0:
            lista_avance_real = lista_avance_real_all[contador_proyecto]
            for avance in lista_avance_real:
                if avance[1] == 0:
                    avance_real = avance[0]
                    contador_real = contador_real + 1
            contador_real = contador_real - 1
            #Obtener avance esperado curva s 
            avance_programado = avance_esperado_all[contador_proyecto][contador_real][0]

            #### Filtros de verificación para notificar a encargados del Proyecto
            last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=4).last()
            delta_proyect = (fecha_actual - last_hu.last_checked)

            if delta_proyect.days >= last_hu.cliente_tiempo_control:
                print("Se notifica para proyecto {}!".format(proyecto.nombre))
                diferencias = []
                diferencia_avance =  float(avance_programado) - float(avance_real)
                
                if last_hu.variable_atraso >= 0:
                    if diferencia_avance >= float(last_hu.cliente_variable_atraso):
                        lista_proyectos_atrasados.append([proyecto, [diferencia_avance, avance_programado, avance_real]])
                if last_hu.variable_atraso < 0:
                    if diferencia_avance <= float(last_hu.cliente_variable_atraso):
                        lista_proyectos_atrasados.append([proyecto, diferencias])

        contador_proyecto = contador_proyecto + 1

    if len(lista_proyectos_atrasados) != 0:
        for proyecto in lista_proyectos_atrasados:
            subject = "[UMBRAL {proyecto}] Atraso Porcentual del Proyecto - {date}".format(proyecto=proyecto[0].codigo, date=timezone.now().strftime("%d-%B-%y"))
            usuarios = users_notifier(proyecto=proyecto[0], cliente=True)
            try:
                send_email(
                    html= 'configuracion/umbral_4.html',
                    context= {
                        "proyecto": proyecto[0],
                        "desviacion": proyecto[1][0],
                        "avance_programado": proyecto[1][1],
                        "avance_real": proyecto[1][2],
                    },
                    subject=subject,
                    recipients= usuarios[0]
                )
                for usuario in usuarios[1]:
                    noti = Notificacion(
                        proyecto=proyecto[0],
                        usuario=usuario,
                        notification_type=1,
                        text_preview=subject
                    )
                    noti.save()

                    noti_hu = NotificacionHU(
                        h_umbral=last_hu,
                        notificacion=noti,
                        porcentaje_atraso=proyecto[1]
                    )
                    noti_hu.save()

                last_hu.last_checked = timezone.now()
                last_hu.save()

            except Exception as err:
                error = "Un error Ocurrido al momento de notificar para el Umbral 4. {}".format(err)
                return error
    else:
        pass

    return lista_proyectos_atrasados
