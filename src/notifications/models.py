from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class Notificacion(models.Model):
	NOTIFICATION_TYPES = ((1,'Proyecto'),(2,'Estado'))

	# proyecto = models.ForeignKey('post.Post', on_delete=models.CASCADE, related_name="noti_post", blank=True, null=True)
	usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_from_user")
	enviador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_to_user")
	notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
	text_preview = models.CharField(max_length=90, blank=True)
	date = models.DateTimeField(auto_now_add=True)
	is_seen = models.BooleanField(default=False)