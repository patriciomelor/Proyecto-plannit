from __future__ import absolute_import, unicode_literals
from bandeja_es.models import Version
from os import name

from dmp.celery import app
from notifications.emails import send_email
from notifications.models import Notificacion
from panel_carga.models import Documento, Proyecto
from configuracion.models import Umbral, HistorialUmbrales, NotificacionHU
from panel_carga.choices import TYPES_REVISION, ESTADOS_CLIENTE, ESTADO_CONTRATISTA
from datetime import datetime, time, timedelta
from django.utils import timezone
import math

# @app.task(name="desviacion")
# def umbral_1(umbral, doc):
#     pass

def users_notifier(proyecto):
    recipients = []
    notification_list = []
    participantes = proyecto.participantes.all()
    for user in participantes:
        rol = user.perfil.rol_usuario
        if rol == 1:
            recipients.append(user.email)
            notification_list.append(user)

    return [recipients, notification_list]

@app.task(name="umbral_2")
def umbral_2():
    proyectos = Proyecto.objects.all()
    for proyecto in proyectos:
        document_list = []


        # last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=2).last()
        # delta_proyect = (datetime.date.today() - last_hu.last_checked)

        # if delta_proyect.days >= last_hu.tiempo_control:
        documentos = Documento.objects.filter(proyecto=proyecto)
        for doc in documentos:
            # delta_doc = (datetime.now() - doc.fecha_Emision_B)
            # if delta_doc.days > 0: #last_hu.variable_atraso:
            document_list.append(doc)

        try:
            subject = "[UMBRAL {proyecto}] Listado de Documentos Atrasados.".format(proyecto=proyecto.nombre)
            send_email(
                html= 'configuracion/umbral_2.html',
                context= {
                    "documentos": document_list,
                    "proyecto": proyecto
                },
                subject=subject,
                recipients= ["patriciomelor@gmail.com", "esteban.martinezs@utem.cl", "ignaciovaldeb1996@gmail.com"]
            )
            # for usuario in notification_list:
            #     noti = Notificacion(
            #         proyecto=proyecto,
            #         usuario=usuario,
            #         notification_type=1,
            #         text_preview=subject
            #     )
            #     noti.save()

            #     # noti_hu = NotificacionHU(
            #     #     h_umbral=last_hu,
            #     #     notificacion=noti,
            #     # )
            #     # noti_hu.save()
            #     # noti_hu.documentos.set(document_list, clear=True)

        except Exception as err:
            error = "Un error Ocurrido al momento de notificar para el Umbral 2. {}".format(err)
            return error
    else:
        pass

    return document_list

@app.task(name="umbral_3")
def umbral_3():

    proyectos = Proyecto.objects.all()
    for proyecto in proyectos:
        revision_list = []
        document_list = []
        recipients = []
        notification_list = []
        participantes = proyecto.participantes.all()
        for user in participantes:
            rol = user.perfil.rol_usuario
            if rol == 4:
                recipients.append(user.email)
                notification_list.append(user)

        # last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=3).last()
        # delta_proyect = (datetime.date.today() - last_hu.last_checked)

        # if delta_proyect.days >= last_hu.tiempo_control:
        documentos = Documento.objects.filter(proyecto=proyecto)
        revisiones = Version.objects.filter(documento_fk__in=documentos)
        for rev in revisiones:
            # delta_rev = (datetime.now() - rev.fecha)
            # if delta_rev.days > 0:  #last_hu.variable_atraso:
            revision_list.append(rev)
            document_list.append(rev.documento_fk)
        
        subject = "[UMBRAL {proyecto}] Listado de Documentos Atrasados.".format(proyecto=proyecto.nombre)
        try:
            send_email(
                html= 'configuracion/umbral_3.html',
                context= {
                    "revisiones": revision_list,
                    "proyecto": proyecto
                },
                subject=subject,
                recipients= ["patriciomelor@gmail.com", "esteban.martinezs@utem.cl", "ignaciovaldeb1996@gmail.com"]
            )
            for usuario in notification_list:
                noti = Notificacion(
                    proyecto=proyecto,
                    usuario=usuario,
                    notification_type=1,
                    text_preview=subject
                )
                noti.save()

                # noti_hu = NotificacionHU(
                #     h_umbral=last_hu,
                #     notificacion=noti,
                # )
                # noti_hu.save()
                # noti_hu.documentos.set(document_list, clear=True)

        except Exception as err:
            error = "Un error Ocurrido al momento de notificar para el Umbral 3. {}".format(err)
            return error
    else:
        pass

    return revision_list


def get_users_dash(proyecto):
    users = proyecto.participantes.all()
    lista_usuarios = []

    for usuarios in users:
        if usuarios.perfil.rol_usuario == 4 or usuarios.perfil.rol_usuario == 5:
            lista_usuarios.append(usuarios)             

    return lista_usuarios

def Obtener_fechas():
    elementos_final = []
    elementos = []
    conjunto_finales = []
    proyectos = Proyecto.objects.all()

    for proyecto in proyectos:
        documentos = Documento.objects.filter(proyecto=proyecto)        
        valor_ganado = Documento.objects.filter(proyecto=proyecto).count()

        if valor_ganado !=0:

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
            elementos = [fechas_controles]
            elementos_final.append(elementos)

        else:
            #Se almacena arreglo de fechas en la lista final
            elementos_final.append([])
        
        conjunto_finales.append(elementos_final)
    
    return conjunto_finales

def reporte_curva_s_avance_real():

    proyectos = Proyecto.objects.all()
    lista_final = Obtener_fechas()
    dia_actual = timezone.now()
    contador_fechas_grupo = 0
    conjunto_finales = []

    for proyecto in proyectos:
        documentos = Documento.objects.filter(proyecto=proyecto)        
        valor_ganado = Documento.objects.filter(proyecto=proyecto).count()
        usuarios = get_users_dash(proyecto=proyecto)
    
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
                version = Version.objects.filter(documento_fk=doc)
                contador = 0
                if version:
                    cont = 0
                    cont2 = 0

                    for versiones in version:
                        for users in usuarios:
                            nombre = users.first_name + ' ' + users.last_name
                            if versiones.revision < 5:
                                if str(nombre) == str(versiones.owner) and cont == 0:               
                                    version_letras = versiones
                                    cont = 1
                            if versiones.revision > 4:
                                if str(nombre) == str(versiones.owner) and cont2 == 0:               
                                    version_numerica = versiones
                                    cont2 = 1

                    if cont == 1 and cont2 == 1:
                        lista_versiones.append([doc, [version_letras, version_numerica]])

                    if cont == 1 and cont2 == 0:
                        lista_versiones.append([doc, [version_letras]])

                    if cont == 0 and cont2 == 1:
                        lista_versiones.append([doc, [version_numerica]])

                if not version:
                    pass
            #Se recorren las versiones a calcular el avance real
            for docs in lista_versiones:
                contador_avance = 0

                for versiones in docs[1]:
                    contador_versiones = contador_versiones + 1
                    fecha_version = versiones.fecha
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
                                fecha_version = versiones.fecha
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
        
        contador_fechas = contador_fechas + 1
        conjunto_finales.append(avance_final)

    return conjunto_finales

def reporte_curva_s_avance_esperado():
                
    lista_final = Obtener_fechas()
    lista_avance_real = reporte_curva_s_avance_real()
    avance_esperado = []
    lista_final_esperado = []
    diferencia = 0
    contador = 0
    numero = 100
    contador_fechas = 0
    conjunto_finales = []

    proyectos = Proyecto.objects.all()
    for proyecto in proyectos:
        documentos = Documento.objects.filter(proyecto=proyecto)        
        valor_ganado = Documento.objects.filter(proyecto=proyecto).count()
    
        if valor_ganado != 0:
            
            #Calculo del avance esperado por fecha de control
            fecha_emision_b = 0
            fecha_emision_0 = 0
            fechas_controles = lista_final[contador_fechas][0][0]
            valor_ganado = (100 / valor_ganado)

            diferencia = len(lista_avance_real[contador_fechas]) - len(fechas_controles)

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

        contador_fechas = contador_fechas + 1
        conjunto_finales.append(lista_final_esperado)

    return conjunto_finales

# def diferencia_porcentual():

#     avance_esperado_all = reporte_curva_s_avance_esperado()
#     lista_avance_real_all = reporte_curva_s_avance_real()
#     contador_real = 0
#     avance_programado = 0
#     avance_real = 0
#     lista_proyectos_atrasados = []

#     proyectos = Proyecto.objects.all()

#     for proyecto in proyectos:
#         documentos = Documento.objects.filter(proyecto=proyecto)        
#         valor_ganado = Documento.objects.filter(proyecto=proyecto).count()
#         contador_proyecto = 0

#         if valor_ganado != 0:
#             lista_avance_real = lista_avance_real_all[contador_proyecto]
#             for avance in lista_avance_real:
#                 if avance[1] == 0:
#                     avance_real = avance[0]
#                     contador_real = contador_real + 1
#                 contador_real = contador_real - 1
#                 #Obtener avance esperado curva s 
#                 avance_programado = avance_esperado_all[contador_proyecto][contador_real][0]
            
#             diferencia_avance = float(avance_real - avance_programado)
#             if diferencia_avance != float(5):
#                 lista_proyectos_atrasados.append(proyecto)

#         if valor_ganado == 0:
#             pass
    
#         contador_proyecto = contador_proyecto + 1
    
#     return lista_proyectos_atrasados


@app.task(name="umbral_4")
def umbral_4():
    avance_esperado_all = reporte_curva_s_avance_esperado()
    lista_avance_real_all = reporte_curva_s_avance_real()
    contador_real = 0
    avance_programado = 0
    avance_real = 0
    lista_proyectos_atrasados = []
    contador_proyecto = 0

    proyectos = Proyecto.objects.all()

    for proyecto in proyectos:   
        valor_ganado = Documento.objects.filter(proyecto=proyecto).count()

        if valor_ganado != 0:
            lista_avance_real = lista_avance_real_all[contador_proyecto]
            for avance in lista_avance_real:
                if avance[1] == 0:
                    avance_real = avance[0]
                    contador_real = contador_real + 1
                contador_real = contador_real - 1
                #Obtener avance esperado curva s 
                avance_programado = avance_esperado_all[contador_proyecto][contador_real]
            
            diferencia_avance = float(avance_real - avance_programado)
            if diferencia_avance > float(20):
                lista_proyectos_atrasados.append(proyecto)

        if valor_ganado == 0:
            pass
    
        contador_proyecto = contador_proyecto + 1
    
    return lista_proyectos_atrasados
