from django.db import models
from django.contrib.auth.models import User

from panel_carga.models import Documento


class Paquete(models.Model):
    documento = models.ManyToManyField(Documento, through='PaqueteDocumento') #Relacion muchos a muchos, se redirecciona a la tabla auxiliar que se indica acá de otra manera no se podrian agregar varias veces los documentos, si bien se podria agregar 2 o mas veces el mismo documento, desconozco si se puede para varios proyectos el mismo documento.
    nombre = models.CharField(verbose_name="Nombre del paquete", max_length=100, blank=False)
    fecha_creacion = models.DateField(verbose_name="Fecha de creacion", auto_now_add=True, editable=True)
    fecha_respuesta = models.DateField(verbose_name="Fecha de respuesta", editable=True) #a que fecha corresponde?
    asunto = models.TextField(verbose_name="Emitida para")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    periodo = models.CharField(verbose_name="Periodo", max_length=20) #ej Agosto 2020

    def __str__(self):
        return self.nombre


class PaqueteDocumento(models.Model): #Tabla auxiliar que basicamente es lo mismo que crea automaticamente django para la realizacion de un many to many, pero customizable a lo que necesitemos, cosa que mas adelante si necesitamos almacenar otra informacion del registro de los paquetes, se puede hacer
    documento_id = models.ForeignKey(Documento, on_delete=models.CASCADE)
    paquete_id = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

