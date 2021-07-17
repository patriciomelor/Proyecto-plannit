from __future__ import absolute_import, unicode_literals
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
    recipients = []
    proyectos = Proyecto.objects.all()
    for proyecto in proyectos:
        participantes = proyecto.participantes.all()
        for user in participantes:
            rol = user.perfil.rol_usuario
            if rol == 1:
                recipients.append(user.email)
        last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto).last()
        delta = (datetime.now() - last_hu.last_checked)
        if delta.days >= proyecto.umbral_documento_atrasado :
            send_email(
                html= 'configuracion/umbral_1.html',
                context= {},
                subject="[UMBRAL] Listado de Documentos Atrasados.",
                recipients=recipients
            )
        else:
            pass


# @app.task(name="umbral_3")
# def umbral_3(umbral, doc):
#     pass

# @app.task(name="umbral_4")
# def umbral_4(umbral, doc):
#     pass

