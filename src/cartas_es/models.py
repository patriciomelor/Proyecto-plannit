from pyexpat import model
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Carta(models.Model):
    fecha_creacion = models.DateField(verbose_name="Fecha de Creación", auto_now_add=True)
    codigo = models.CharField(max_length=100, verbose_name='Codigo de la Carta', unique=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Destinatario")
    asunto = models.CharField(verbose_name="Asunto", max_length=256)
    cuerpo = models.TextField(verbose_name="Cuerpo", blank=True, null=True)
    anexo = models.FileField(verbose_name="Anexo", upload_to="cartas/anexos")
    contestado = models.BooleanField(verbose_name="Contestado", default=0, blank=True)

    def __str__(self):
        return "Carta" + str(self.codigo)

class CartaRespuesta(models.Model):
    fecha_creacion = models.DateField(verbose_name="Fecha de Creación", auto_now_add=True)
    codigo = models.CharField(max_length=100, verbose_name='Codigo de la CartaRespuesta', unique=True)
    carta = models.ManyToManyField(Carta, blank=True, verbose_name="Carta de Origen")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Destinatario")
    asunto = models.CharField(verbose_name="Asunto", max_length=256)
    cuerpo = models.TextField(verbose_name="Cuerpo", blank=True, null=True)
    anexo = models.FileField(verbose_name="Anexo", upload_to="cartas/respuesta/anexos")
