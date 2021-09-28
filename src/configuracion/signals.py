import datetime
from django.utils import timezone
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from notifications.emails import send_email
from configuracion.models import HistorialUmbrales, NotificacionHU, Umbral
from notifications.models import Notificacion

from bandeja_es.models import Version


def get_users(proyecto):
    recipients = []
    notification_list = []
    participantes = proyecto.participantes.all()
    for usuario in participantes:
        recipients.append(usuario.email)
        notification_list.append(usuario)

    return [recipients, notification_list]

@receiver(post_save, sender=Version)
def VPC_signal(sender, instance, *args, **kwargs):
    notified = []
    current = instance
    try:
        previous = Version.objects.filter(documento_fk=instance.documento_fk).reverse()[1]
    except Version.DoesNotExist:
        print('No existe una Versión todavía.') 
        previous = None

    if not previous == None:
        if previous.estado_cliente == 5:
            if previous.revision != current.revision:                
                try:
                    proyecto = instance.documento_fk.proyecto
                    usuarios = get_users(proyecto=proyecto)
                    subject = "[UMBRAL {proyecto}] Documento Actualizado - {date}.".format(proyecto=proyecto.codigo, date=timezone.now().strftime("%d-%B-%y"))

                    send_email(
                        html= 'configuracion/umbral_1.html',
                        context= {
                            "revision": instance,
                        },
                        subject=subject,
                        recipients= usuarios[0]
                    )

                    last_hu = HistorialUmbrales.objects.filter(proyecto=proyecto, umbral__pk=1).last()
                    last_hu.last_checked = timezone.now()
                    last_hu.save()

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
                        noti_hu.versiones.add(current)
                        noti_hu.documentos.add(current.documento_fk)
                        
                        aux = [usuario, proyecto]
                        notified.append(aux)
                    
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

    return notified
