from panel_carga.models import Proyecto
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Notificacion(models.Model):
	NOTIFICATION_TYPES = ((1,'Umbral'),(2,'Transmittal'), (3,'Tarea'))

	proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="notificacion_proyecto", blank=True, null=True)
	usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_user")
	notification_type = models.IntegerField(verbose_name="tipo notificación", choices=NOTIFICATION_TYPES)
	text_preview = models.CharField(verbose_name="texto", max_length=90, blank=True)
	date = models.DateTimeField(verbose_name="fecha envio", auto_now_add=True)
	is_seen = models.BooleanField(verbose_name="visto", default=False)
	
