from django.db import models
from django.contrib.auth.models import User
from panel_carga.choices import ESTADO_CONTRATISTA,ESTADOS_CLIENTE

from panel_carga.models import Documento


class Paquete(models.Model):
    documento = models.ManyToManyField(Documento, through='PaqueteDocumento') #Relacion muchos a muchos, se redirecciona a la tabla auxiliar que se indica acá de otra manera no se podrian agregar varias veces los documentos, si bien se podria agregar 2 o mas veces el mismo documento, desconozco si se puede para varios proyectos el mismo documento.
    fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=True)
    fecha_respuesta = models.DateTimeField(verbose_name="Fecha de respuesta", editable=True, blank=True, null=True) #a que fecha corresponde?
    asunto = models.CharField(verbose_name="Asunto", max_length=50)
    descripcion = models.CharField(verbose_name="Descripcion", max_length=500, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="propietario")
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="destinatario")
    status = models.BooleanField(verbose_name="Status", default=0, blank=True)

    def __str__(self):
        return self.nombre


class PaqueteDocumento(models.Model): #Tabla auxiliar que basicamente es lo mismo que crea automaticamente django para la realizacion de un many to many, pero customizable a lo que necesitemos, cosa que mas adelante si necesitamos almacenar otra informacion del registro de los paquetes, se puede hacer
    documento_id = models.ForeignKey(Documento, on_delete=models.CASCADE)
    paquete_id = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.documento_id.Descripcion)

class Borrador(models.Model):
    documento = models.ManyToManyField(Documento, through='BorradorDocumento') #Relacion muchos a muchos, se redirecciona a la tabla auxiliar que se indica acá de otra manera no se podrian agregar varias veces los documentos, si bien se podria agregar 2 o mas veces el mismo documento, desconozco si se puede para varios proyectos el mismo documento.
    nombre = models.CharField(verbose_name="Nombre", max_length=100, blank=False)
    fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=True)
    asunto = models.CharField(verbose_name="Asunto", max_length=50)
    descripcion = models.CharField(verbose_name="Descripcion", max_length=200, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="propietario_borrador")
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="destinatario_borrador")
    
    def __str__(self):
        return self.nombre

class BorradorDocumento(models.Model):
    documento_id = models.ForeignKey(Documento, on_delete=models.CASCADE)
    borrador_id = models.ForeignKey(Borrador, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=False)
    
    def __str__(self):
        return str(self.documento_id.Descripcion)

class Version(models.Model):
    fecha = models.DateTimeField(verbose_name="Fecha Version", auto_now_add=True)
    comentario = models.FileField(upload_to="proyecto/comentarios/", blank=True)
    documento_fk = models.ForeignKey(Documento, on_delete=models.CASCADE) #relacion por defecto one to many en django
    archivo = models.FileField(upload_to="proyecto/documentos/", blank=True)
    revision = models.CharField(verbose_name="Emicion/Revision", max_length=1, default="B")
    estado_cliente = models.IntegerField(choices=ESTADOS_CLIENTE, default=1, blank=True)
    estado_contratista = models.IntegerField(choices=ESTADO_CONTRATISTA, default=1, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creador", default=1)
    paquete_fk = models.ForeignKey(Paquete, on_delete=models.CASCADE, verbose_name=Paquete)
    valido = models.BooleanField(verbose_name="Valido", default=1) #1=VALIDO  0=ANULADO

    def __str__(self):
        return str(self.documento_fk.Especialidad + self.revision)

    