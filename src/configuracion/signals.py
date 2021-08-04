import datetime
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from notifications.emails import send_email
from configuracion.models import NotificacionHU
from notifications.models import Notificacion

from bandeja_es.models import Version

@receiver(post_save, sender=Version)
def VPC_signal(sender, instance, created, *args, **kwargs):
    if instance.estado_cliente == 5:
        recipients = []
        notification_list = []
        proyecto = instance.documento_fk.proyecto
        participantes = proyecto.participante.all()
        for user in participantes:
            rol = user.perfil.rol_usuario
            if rol == 1:
                recipients.append(user.email)
                notification_list.append(user)
        
        subject = "[UMBRAL {proyecto}] Documento Actualizado como Válido para Construcción - {date}.".format(proyecto=proyecto.nombre, date=datetime.date.today().days.strftime("%d-%B-%y"))

        try:
            send_email(
                html= 'configuracion/umbral_2.html',
                context= {
                    "revision": instance,
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
        except Exception as err:
            error = "Un error Ocurrido al momento de notificar para el Umbral 1. {}".format(err)
            print(error)
            return error
    else:
        pass

    return instance
