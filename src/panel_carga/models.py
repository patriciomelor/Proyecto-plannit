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
   
class Estado(models.Model):
    estado = models.IntegerField(verbose_name="estado",null=False)
    fecha_inicio = models.DateTimeField(verbose_name="Fecha_de_Inicio", editable=False, null=False)
    fecha_temrino = models.DateTimeField(verbose_name="Fecha_de_Termino", blank=True)
    
    def __str__(self):
        return str(self.estado)

class Revision(models.Model):
    tipo = models.CharField(verbose_name="Tipo_Revision", max_length=50, null=False)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=False)
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



