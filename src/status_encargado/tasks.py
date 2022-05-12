from __future__ import absolute_import, unicode_literals

import math
from datetime import date, datetime, time, timedelta
from os import name

from celery.utils.functional import pass1

from analitica.models import CurvasBase
from bandeja_es.models import Version
from django.utils import timezone
from dmp.celery import app
from notifications.emails import send_email
from notifications.models import Notificacion
from panel_carga.choices import (ESTADO_CONTRATISTA, ESTADOS_CLIENTE,
                                 TYPES_REVISION)
from panel_carga.models import Proyecto

from configuracion.models import HistorialUmbrales, NotificacionHU, Umbral
from .models import Tarea


def get_admin_emails(admins):
    recipient_list=[]
    for user in admins:
        recipient_list.append(str(user.email))

    return recipient_list

@app.task(name="umbral_5_tareas")
def umbral_tareas_atrasadas():
    proyectos = Proyecto.objects.all()
    fecha_actual = timezone.now()

    for proyecto in proyectos:
        last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=5).last()
        delta_proyect = (fecha_actual - last_hu.last_checked)

        if delta_proyect.days >= last_hu.cliente_tiempo_control:
            users =  proyecto.participantes.select_related("perfil").all()
            admins =  users.filter(perfil__rol_usuario=1, is_superuser=False)
            for usuario in users:
                tareas_notificar = []
                tareas_atrasadas = Tarea.objects.filter(encargado=usuario, estado=False)
                for tarea in tareas_atrasadas:
                    delta_late_days = (date.today() - tarea.plazo) 
                    tareas_notificar.append([tarea, delta_late_days])
                notf_admins = get_admin_emails(admins=admins)
                notf_admins.append(usuario.email)
                subject = "[UMBRAL {proyecto}] Tareas atrasadas. ".format(proyecto=proyecto.codigo)
                send_email(
                    html= "status_encargado/listado_tareas_umbral.html",
                    context= {
                        "tareas": tareas_atrasadas,
                        "proyecto": proyecto,
                        "usuario": usuario,
                    },
                    subject=subject, 
                    recipients=notf_admins
                )
        else:
            pass

        if delta_proyect.days >= last_hu.contratista_tiempo_control:
            users =  proyecto.participantes.select_related("perfil").all()
            admins =  users.filter(perfil__rol_usuario=4, is_superuser=False)
            for usuario in users:
                tareas_notificar = []
                tareas_atrasadas = Tarea.objects.filter(encargado=usuario, estado=False)
                for tarea in tareas_atrasadas:
                    delta_late_days = (date.today() - tarea.plazo) 
                    tareas_notificar.append([tarea, delta_late_days])
                
                notf_admins = get_admin_emails(admins=admins)
                notf_admins.append(usuario.email)
                subject = "[UMBRAL {proyecto}] Tareas atrasadas. ".format(proyecto=proyecto.codigo)
                send_email(
                    html= "status_encargado/listado_tareas_umbral.html",
                    context= {
                        "tareas": tareas_notificar,
                        "proyecto": proyecto,
                        "usuario": usuario,
                    },
                    subject=subject, 
                    recipients=notf_admins
                )
        else:
            pass