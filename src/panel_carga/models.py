from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Proyecto(models.Model):
    nombre = models.CharField(verbose_name="Nombre del Proyecto", max_length=50, null=False)
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio", null=False)
    fecha_temrino = models.DateField(verbose_name="Fecha de Termino", blank=True)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre
   
class Revision(models.Model):

    ESTADOS_CLIENTE = (
        (1, "Aprobado con Comentarios"),
        (2, "Rechazado"), 
        (3, "Eliminado"),
        (4, "Aprobado"),
        (5, "Valido para construcción"),
        (6, "Aprobado"),
    )

    ESTADO_CONTRATISTA =  (
        (1, "Para revisión"),
        (2, "Para aprobación"),
    )

    tipo = models.CharField(verbose_name="Tipo_Revision", max_length=50, null=False)
    estado_cliente = models.IntegerField(choices=ESTADOS_CLIENTE, default=1)
    estado_contratista = models.IntegerField(choices=ESTADO_CONTRATISTA, default=1)
    emitida_para = models.TextField(verbose_name="Emitida_para")
    fecha = models.DateTimeField(verbose_name="Fecha", editable=False, null=False)

    def __str__(self):
        return self.tipo

class Documento(models.Model):
    nombre = models.CharField(verbose_name="Nombre_del_Documento", max_length=100, null=False)
    especialidad = models.CharField(verbose_name="Especialidad", max_length=100, null=False)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    num_documento = models.CharField(verbose_name="Número de Documento", max_length=100, null=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    emision = models.ForeignKey(Revision, on_delete=models.CASCADE, null=True)
    tipo = models.CharField(verbose_name="Típo de Documento", max_length=50, null=False)
    archivo = models.FileField(upload_to="proyecto/documentos/", null=True)

    def __str__(self):
        return self.nombre



