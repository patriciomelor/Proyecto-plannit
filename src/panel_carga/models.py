from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Proyecto(models.Model):
    nombre = models.CharField(verbose_name="Nombre del Proyecto", max_length=50, null=False)
    fecha_inicio = models.DateTimeField(verbose_name="Fecha de Inicio", editable=False, null=False)
    fecha_temrino = models.DateTimeField(verbose_name="Fecha de Termino", blank=True)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre
    

class Documento(models.Model):
    nombre = models.CharField(verbose_name="Nombre del Documento", max_length=100, null=False)
    especialidad = models.CharField(verbose_name="Especialidad", max_length=100, null=False)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    num_documento = models.CharField(verbose_name="Número de Documento", max_length=100, null=False)
    archivo = models.FileField(upload_to="proyecto/documentos/")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre