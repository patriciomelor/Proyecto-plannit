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
    encargado = models.ForeignKey(User, on_delete=models.CASCADE)
    #dias para revision

    def __str__(self):
        return self.nombre

    def toJSON(self):
        item = model_to_dict(self)
        item['Nombre'] = self.nombre
        item['Fecha Inicio'] = self.fecha_inicio
        item['Fecha Termino'] = self.fecha_termino
        return item

class Documento(models.Model):
    
    Especialidad = models.CharField(verbose_name="Especialidad", max_length=100, blank=False)
    Descripcion = models.TextField(verbose_name="Descripción", blank=False)
    Codigo_documento = models.CharField(verbose_name="Codigo Documento",unique=True, max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    Tipo_Documento = models.CharField(verbose_name="Tipo Documento", max_length=50)
    Numero_documento_interno = models.CharField(verbose_name="Numero documento Interno", max_length=50, blank=True)
    archivo = models.FileField(upload_to="proyecto/documentos/", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_Emision_B = models.DateTimeField(verbose_name="Fecha inicio emisión", blank=True, default=None) 
    fecha_Emision_0 = models.DateTimeField(verbose_name="Fecha inicio emisión", blank=True, default=None) 
    


    def __str__(self):
        return self.Codigo_documento
    
    def toJSON(self):
        item = model_to_dict(self)
        item['Codigo Documento'] = self.Codigo_documento
        item['Fecha Emision B'] = self.fecha_Emision_B
        return item





#Tabla que almacena el historico de las ediciones por documento, la idea es mostrar siempre el ultimo para saber quien le metio mano a ese documento
#De ser necesario tambien se puede revisar quien lo hizo antes, pero la idea es que este restringida su vista al ultimo 
#por ende esta tabla deberia mejorar 
class Historial(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True) #Quien lo edito
    fecha = models.DateTimeField(verbose_name="Fecha ultima edicion", editable=False, blank=True) #fecha de la edicion
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, blank=True) 

    def __str__(self):
        return self.fecha
    
    def toJSON(self):
        item = model_to_dict(self)
        item['Codigo Documento'] = self.documento
        item['Fecha'] = self.fecha
        return item


class Revision(models.Model):

    tipo = models.IntegerField(choices=TYPES_REVISION, verbose_name="Tipo Revision", default=1)
    estado_cliente = models.IntegerField(choices=ESTADOS_CLIENTE, default=1)
    estado_contratista = models.IntegerField(choices=ESTADO_CONTRATISTA, default=1)
    emitida_para = models.TextField(verbose_name="Emitida para")
    fecha = models.DateTimeField(verbose_name="Fecha", editable=False)
    fecha_estimada = models.DateTimeField(verbose_name="Fecha rev 0", editable=True, default='2021-01-01') #preguntar a davis por el calculo de los dias
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, blank=True, default=5) #Hay que dar vuelta la relacion 

    def __str__(self):
        return self.tipo

    def toJSON(self):
        item = model_to_dict(self)
        item['Codigo Documento'] = self.documento
        item['Fecha'] = self.fecha
        item['Emitida Para'] = self.emitida_para
        return item
