from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from .choices import (ESTADO_CONTRATISTA,ESTADOS_CLIENTE,TYPES_REVISION, DOCUMENT_TYPE)


# Create your models here.

class Proyecto(models.Model):

    nombre = models.CharField(verbose_name="Nombre del Proyecto", max_length=50, unique=True)
    fecha_inicio = models.DateTimeField(verbose_name="Fecha de Inicio")
    fecha_termino = models.DateTimeField(verbose_name="Fecha de Termino", blank=True)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Encargado")
    codigo = models.CharField(max_length=100, verbose_name='Codigo del Proyecto', unique=True)
    participantes = models.ManyToManyField(User, related_name="participantes")
    umbral_documento_aprobado = models.IntegerField(verbose_name="Umbral para Documentos Aprobados")
    umbral_documento_atrasado = models.IntegerField(verbose_name="Umbral para Documentos Atrasados")
    umbral_revision_documento = models.IntegerField(verbose_name="Umbral para Revisiones Atrasadas")
    umbral_desviacion_porcentual = models.FloatField(verbose_name="Umbral para Dviación Porcentual del Proyecto")
    #dias para revision


    def __str__(self):
        return self.nombre


class Documento(models.Model):
    
    Especialidad = models.CharField(verbose_name="Especialidad", max_length=100, blank=False)
    Descripcion = models.TextField(verbose_name="Descripción", blank=False)
    Codigo_documento = models.CharField(verbose_name="Codigo Documento",unique=True, max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    Tipo_Documento = models.CharField(verbose_name="Tipo Documento", max_length=50)
    Numero_documento_interno = models.CharField(verbose_name="Numero documento Interno", max_length=50, blank=True, null=True)
    archivo = models.FileField(upload_to="proyecto/documentos/", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_Emision_B = models.DateTimeField(verbose_name="Fecha inicio emisión B", blank=True, default=None) 
    fecha_Emision_0 = models.DateTimeField(verbose_name="Fecha inicio emisión 0", blank=True, default=None) 
    


    def __str__(self):
        return self.Codigo_documento
    

#Tabla que almacena el historico de las ediciones por documento, la idea es mostrar siempre el ultimo para saber quien le metio mano a ese documento
#De ser necesario tambien se puede revisar quien lo hizo antes, pero la idea es que este restringida su vista al ultimo 
#por ende esta tabla deberia mejorar 
class Historial(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True) #Quien lo edito
    fecha = models.DateTimeField(verbose_name="Fecha ultima edicion", editable=False, blank=True) #fecha de la edicion
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, blank=True) 

    def __str__(self):
        return self.fecha


class Revision(models.Model):
    tipo = models.CharField(verbose_name="Letra o Número", max_length=1)
    porcentaje = models.FloatField(verbose_name="Porcentaje de Avance")
    
    def __str__(self):
        return self.tipo