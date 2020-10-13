from django.db import models
from django.contrib.auth.models import User
from .choices import ESTADO_CONTRATISTA,ESTADOS_CLIENTE,TYPES_REVISION,DOCUMENT_TYPE


# Create your models here.

class Proyecto(models.Model):

    nombre = models.CharField(verbose_name="Nombre del Proyecto", max_length=50, null=False, unique=True)
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio", null=False)
    fecha_termino = models.DateField(verbose_name="Fecha de Termino", blank=True)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre
   
class Revision(models.Model):

    tipo = models.IntegerField(choices=TYPES_REVISION, verbose_name="Tipo Revision", null=False, default=1)
    estado_cliente = models.IntegerField(choices=ESTADOS_CLIENTE, default=1)
    estado_contratista = models.IntegerField(choices=ESTADO_CONTRATISTA, default=1)
    emitida_para = models.TextField(verbose_name="Emitida para")
    fecha = models.DateField(verbose_name="Fecha", editable=False, null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.tipo
    
#Tabla que almacena el historico de las ediciones por documento, la idea es mostrar siempre el ultimo para saber quien le metio mano a ese documento
#De ser necesario tambien se puede revisar quien lo hizo antes, pero la idea es que este restringida su vista al ultimo 
#por ende esta tabla deberia mejorar 
class Historial(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=True) #Quien lo edito
    fecha = models.DateField(verbose_name="Fecha ultima edicion", editable= False, null=False, blank=True) #fecha de la edicion


    def __str__(self):
        return self.fecha

class Documento(models.Model):
    
    nombre = models.CharField(verbose_name="Nombre del Documento", max_length=100, null=False, unique=True) #deberia ir un editable=False? debido a que no deberia cambiarse el nombre de un documento
    especialidad = models.CharField(verbose_name="Especialidad", max_length=100, null=False)
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    num_documento = models.CharField(verbose_name="Codigo Documento", max_length=100, null=False, unique=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    emision = models.ForeignKey(Revision, on_delete=models.CASCADE, null=True)
    tipo = models.IntegerField(choices=DOCUMENT_TYPE, default=1, null=False)
    archivo = models.FileField(upload_to="proyecto/documentos/", null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    ultima_edicion = models.ForeignKey(Historial, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.nombre




