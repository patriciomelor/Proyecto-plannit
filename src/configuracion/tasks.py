from __future__ import absolute_import, unicode_literals
from bandeja_es.models import Version
from os import name

import datetime
from dmp.celery import app
from notifications.emails import send_email
from notifications.models import Notificacion
from panel_carga.models import Documento, Proyecto
from configuracion.models import Umbral, HistorialUmbrales, NotificacionHU

# @app.task(name="desviacion")
# def umbral_1(umbral, doc):
#     pass

@app.task(name="umbral_2")
def umbral_2():
    document_list = []
    proyectos = Proyecto.objects.all()
    for proyecto in proyectos:
        recipients = []
        notification_list = []
        participantes = proyecto.participantes.all()
        for user in participantes:
            rol = user.perfil.rol_usuario
            if rol == 1:
                recipients.append(user.email)
                notification_list.append(user)

        last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=2).last()
        delta_proyect = (datetime.date.today() - last_hu.last_checked)

        if delta_proyect.days >= last_hu.tiempo_control:
            documentos = Documento.objects.filter(proyecto=proyecto)
            for doc in documentos:
                delta_doc = (datetime.date.today()- doc.fecha_Emision_B)
                if delta_doc.days > last_hu.variable_atraso:
                    document_list.append(doc)
            subject = "[UMBRAL {proyecto}] Listado de Documentos Atrasados - {date}.".format(proyecto=proyecto.nombre, date=datetime.date.today().days.strftime("%d-%B-%y"))
            try:
                send_email(
                    html= 'configuracion/umbral_2.html',
                    context= {
                        "documentos": document_list,
                    },
                    subject=subject,
                    recipients= recipients
                )
                for usuario in notification_list:
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
            except Exception as err:
                error = "Un error Ocurrido al momento de notificar para el Umbral 2. {}".format(err)
                return error
        else:
            pass

    return document_list

@app.task(name="umbral_3")
def umbral_3():
    revision_list = []
    document_list = []
    proyectos = Proyecto.objects.all()
    for proyecto in proyectos:
        recipients = []
        notification_list = []
        participantes = proyecto.participantes.all()
        for user in participantes:
            rol = user.perfil.rol_usuario
            if rol == 4:
                recipients.append(user.email)
                notification_list.append(user)

        last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=3).last()
        delta_proyect = (datetime.date.today() - last_hu.last_checked)

        if delta_proyect.days >= last_hu.tiempo_control:
            documentos = Documento.objects.filter(proyecto=proyecto)
            revisiones = Version.objects.filter(documento_fk__in=documentos)
            for rev in revisiones:
                delta_rev = (datetime.date.today() - rev.fecha)
                if delta_rev.days > last_hu.variable_atraso:
                    revision_list.append(rev)
                    document_list.append(rev.documento_fk)
            subject = "[UMBRAL {proyecto}] Listado de Revisiones Atrasadas - {date}.".format(proyecto=proyecto.nombre, date=datetime.date.today().days.strftime("%d-%B-%y"))
            try:
                send_email(
                    html= 'configuracion/umbral_2.html',
                    context= {
                        "revisiones": revision_list,
                    },
                    subject=subject,
                    recipients= recipients
                )
                for usuario in notification_list:
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

            except Exception as err:
                error = "Un error Ocurrido al momento de notificar para el Umbral 3. {}".format(err)
                return error
        else:
            pass

    return revision_list


# @app.task(name="umbral_4")
# def umbral_4(umbral, doc):
#     pass



        # documentos = Documento.objects.filter(proyecto=proyecto)
        # for doc in documentos:
        #     delta_doc = (timezone.now().strptime(timezone.now(),"%d-%m-%y") - doc.fecha_Emision_B.strptime(doc.fecha_Emision_B, "%d-%m-%y"))
        #     if delta_doc.days > 0:
        #         document_list.append(doc)
