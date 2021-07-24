from __future__ import absolute_import, unicode_literals
from os import name

import datetime
from django.utils import timezone
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
        # recipients = []
        # participantes = proyecto.participantes.all()
        # for user in participantes:
        #     rol = user.perfil.rol_usuario
        #     if rol == 1:
        #         recipients.append(user.email)

        # last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=2).last()
        # delta_proyect = (timezone.now().strftime("%d-%m-%y") - last_hu.last_checked.strftime("%d-%m-%y"))

        # if delta_proyect.days >= last_hu.tiempo_control:
        #     documentos = Documento.objects.filter(proyecto=proyecto)
        #     for doc in documentos:
        #         delta_doc = (timezone.now().strftime("%d-%m-%y") - doc.fecha_Emision_B.strftime("%d-%m-%y"))
        #         if delta_doc.days > last_hu.variable_atraso:
        #             document_list.append(doc)
        documentos = Documento.objects.filter(proyecto=proyecto)
        for doc in documentos:
            delta_doc = (timezone.now().strftime("%d-%m-%y") - doc.fecha_Emision_B.strftime("%d-%m-%y"))
            if delta_doc.days > 0:
                document_list.append(doc)

        send_email(
            html= 'configuracion/umbral_2.html',
            context= {
                "documentos": document_list,
            },
            subject="[UMBRAL {proyecto}] Listado de Documentos Atrasados - {date}.".format(proyecto=proyecto.nombre, date=timezone.now().strftime("%d-%B-%y")),
            recipients= 'patriciomelor@gmail.com' #recipients
        )
        # else:
        #     pass
    return document_list

# @app.task(name="umbral_3")
# def umbral_3(umbral, doc):
#     pass

# @app.task(name="umbral_4")
# def umbral_4(umbral, doc):
#     pass

