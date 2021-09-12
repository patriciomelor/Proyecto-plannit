import datetime
from django.utils import timezone
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from notifications.emails import send_email
from configuracion.models import HistorialUmbrales, NotificacionHU, Umbral
from notifications.models import Notificacion

from bandeja_es.models import Version

@receiver(pre_save, sender=Version)
def VPC_signal(sender, instance, *args, **kwargs):

    current = instance
    try:
        last = Version.objects.filter(documento_fk=instance.documento_fk).last()        
    except Version.DoesNotExist:
        print('No existe una Versión todavía.') 
        last = None

    if not last == None:
        if last.estado_cliente == 5:
            if last.revision != current.revision :
                recipients = []
                notification_list = []
                proyecto = instance.documento_fk.proyecto
                participantes = proyecto.participantes.all()
                for user in participantes:
                    recipients.append(user.email)
                    notification_list.append(user)
                
                subject = "[UMBRAL {proyecto}] Documento Actualizado - {date}.".format(proyecto=proyecto.nombre, date=timezone.now().strftime("%d-%B-%y"))

                try:
                    send_email(
                        html= 'configuracion/umbral_1.html',
                        context= {
                            "revision": instance,
                        },
                        subject=subject,
                        recipients= recipients
                    )

                    last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=1).last()
                    last_hu.last_checked = timezone.now()
                    last_hu.save()

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
                        noti_hu.versiones.add(instance)
                        print("notification added")

                    return instance

                except Exception as err:
                    error = "Un error Ocurrido al momento de notificar para el Umbral 1. {}".format(err)
                    print(error)
                    return error
            
            else:
                pass
        else:
            pass
    else:
        pass