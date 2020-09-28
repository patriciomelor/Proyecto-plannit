from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Proyecto(models.Model):
    id_proyecto = models.AutoField(verbose_name="id_proyecto",primary_key=True)
    nombre = models.CharField(verbose_name="Nombre_del_Proyecto", max_length=50, null=False)
    fecha_inicio = models.DateTimeField(verbose_name="Fecha_de_Inicio", editable=False, null=False)
    fecha_termino = models.DateTimeField(verbose_name="Fecha_de_Termino", blank=True)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre
   

class Documento(models.Model):
    id_Documento = models.AutoField(verbose_name="id_Documento",primary_key=True)
    nombre = models.CharField(verbose_name="Nombre_del_Documento", max_length=100, null=False)
    especialidad = models.CharField(verbose_name="Especialidad", max_length=100, null=False)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    num_documento = models.CharField(verbose_name="Número_de_Documento", max_length=100, null=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=False)
    emision = models.ForeignKey(Revision, on_delete=models.CASCADE, null=False)
    tipo = models.CharField(verbise_name="tipo_documento", max_length=50,null=False)
    archivo = models.FileField(upload_to="proyecto/documentos/")

    def __str__(self):
        return self.nombre

class Revision(models.model):
    id_revision = models.AutoField(verbose_name="id_Revision", primary_key=True)
    tipo = models.CharField(verbose_name="Tipo_Revision", max_length="50", null=False)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=False)
    emitida_para = models.TextField(verbose_name="Emitida_para")
    fecha = models.DateTimeField(verbose_name="Fecha", editable=False, null=False)

    def __str__(self):
        return self.nombre

class Estado(models.model):
    id_estado = models.AutoField(verbose_name="Id_estado", primary_key=True)
    estado = models.IntegerField(verbose_name="estado",null=False)
    fecha_inicio = models.DateTimeField(verbose_name="Fecha_de_Inicio", editable=False, null=False)
    fecha_temrino = models.DateTimeField(verbose_name="Fecha_de_Termino", blank=True)
    
    def __str__(self):
        return self.nombre