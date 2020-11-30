from django.db import models
from django.contrib.auth.models import User
from panel_carga.choices import ESTADO_CONTRATISTA,ESTADOS_CLIENTE

from panel_carga.models import Documento
from django.forms import model_to_dict


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
        return self.fecha_creacion


class PaqueteDocumento(models.Model): #Tabla auxiliar que basicamente es lo mismo que crea automaticamente django para la realizacion de un many to many, pero customizable a lo que necesitemos, cosa que mas adelante si necesitamos almacenar otra informacion del registro de los paquetes, se puede hacer
    documento_id = models.ForeignKey(Documento, on_delete=models.CASCADE)
    paquete_id = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.documento_id.Descripcion)

    def toJSON(self):
        item = model_to_dict(self)
        item['Documento'] = self.documento_id
        item['Fecha Creacion'] = self.fecha_creacion
        item['Paquete'] = self.paquete_id
        return item

class Borrador(models.Model):
    documento = models.ManyToManyField(Documento, through='BorradorDocumento', blank=True) #Relacion muchos a muchos, se redirecciona a la tabla auxiliar que se indica acá de otra manera no se podrian agregar varias veces los documentos, si bien se podria agregar 2 o mas veces el mismo documento, desconozco si se puede para varios proyectos el mismo documento.
    nombre = models.CharField(verbose_name="Nombre", max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=True, blank=True, null=True)
    asunto = models.CharField(verbose_name="Asunto", max_length=50, blank=True, null=True)
    descripcion = models.CharField(verbose_name="Descripcion", max_length=200, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="propietario_borrador", blank=True, null=True)
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="destinatario_borrador", blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class BorradorDocumento(models.Model): # Una vez almacenado debe quedar este registro si o si, por ende no debe ser ninguno blank=True, null=True
    documento_id = models.ForeignKey(Documento, on_delete=models.CASCADE)
    borrador_id = models.ForeignKey(Borrador, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=False)
    
    def __str__(self):
        return str(self.documento_id.Descripcion)
    
    def toJSON(self):
        item = model_to_dict(self)
        item['Documento'] = self.documento_id
        item['Fecha Creacion'] = self.fecha_creacion
        return item

class BorradorVersion(models.Model):
    fecha = models.DateTimeField(verbose_name="Fecha Version", auto_now_add=True, null=True)
    comentario = models.FileField(upload_to="proyecto/comentarios/", blank=True, null=True)
    documento_fk = models.ForeignKey(Documento, on_delete=models.CASCADE) #relacion por defecto one to many en django
    archivo = models.FileField(upload_to="proyecto/documentos/", blank=True, null=True)
    revision = models.CharField(verbose_name="Emicion/Revision", max_length=1, default="B", blank=True, null=True)
    estado_cliente = models.IntegerField(choices=ESTADOS_CLIENTE, default=1, blank=True, null=True)
    estado_contratista = models.IntegerField(choices=ESTADO_CONTRATISTA, default=1, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creador", blank=True, null=True)
    paquete_fk = models.ForeignKey(Borrador, on_delete=models.CASCADE, verbose_name="Paquete Borrador", blank=True, null=True)

    def __str__(self):
        return str(self.documento_fk.Especialidad + self.revision)

class Version(models.Model):
    fecha = models.DateTimeField(verbose_name="Fecha Version", auto_now_add=True)
    comentario = models.FileField(upload_to="proyecto/comentarios/", blank=True)
    documento_fk = models.ForeignKey(Documento, on_delete=models.CASCADE) #relacion por defecto one to many en django
    archivo = models.FileField(upload_to="proyecto/documentos/", blank=True)
    revision = models.CharField(verbose_name="Emicion/Revision", max_length=1, default="B")
    estado_cliente = models.IntegerField(choices=ESTADOS_CLIENTE, default=1, blank=True)
    estado_contratista = models.IntegerField(choices=ESTADO_CONTRATISTA, default=1, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creador")
    paquete_fk = models.ForeignKey(Paquete, on_delete=models.CASCADE, verbose_name=Paquete)
    valido = models.BooleanField(verbose_name="Valido", default=1) #1=VALIDO  0=ANULADO

    def __str__(self):
        return str(self.documento_fk.Especialidad + self.revision)
    
    def toJSON(self):
        item = model_to_dict(self)
        item['Documento'] = self.documento_fk
        item['Fecha Creacion'] = self.fecha
        item['Paquete'] = self.paquete_id
        item['Revision'] = self.revision
        item['Paquete'] = self.paquete_fk
        return item

# INICIO DE PREVISUALIZACION
# PREVISUALIZACION DEL PAQUETE
class PrevPaquete(models.Model):
    prev_documento = models.ManyToManyField(Documento, through='PrevPaqueteDocumento') #Relacion muchos a muchos, se redirecciona a la tabla auxiliar que se indica acá de otra manera no se podrian agregar varias veces los documentos, si bien se podria agregar 2 o mas veces el mismo documento, desconozco si se puede para varios proyectos el mismo documento.
    prev_fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True)
    prev_fecha_respuesta = models.DateTimeField(verbose_name="Fecha de respuesta", editable=True, blank=True, null=True) #a que fecha corresponde?
    prev_asunto = models.CharField(verbose_name="Asunto", max_length=50)
    prev_descripcion = models.CharField(verbose_name="Descripcion", max_length=500, blank=True, null=True)
    prev_propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prevpropietario")
    prev_receptor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prevdestinatario")
    prev_status = models.BooleanField(verbose_name="Status", default=0, blank=True)

    def __str__(self):
        return self.prev_fecha_creacion

# PREVISUALIZACION DEL PAQUETEDOCUMENTO
class PrevPaqueteDocumento(models.Model): #Tabla auxiliar que basicamente es lo mismo que crea automaticamente django para la realizacion de un many to many, pero customizable a lo que necesitemos, cosa que mas adelante si necesitamos almacenar otra informacion del registro de los paquetes, se puede hacer
    prev_documento_id = models.ForeignKey(Documento, on_delete=models.CASCADE)
    prev_paquete_id = models.ForeignKey(PrevPaquete, on_delete=models.CASCADE)
    prev_fecha_creacion = models.DateTimeField(verbose_name="Fecha de creacion", auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.prev_documento_id.Descripcion)

    def toJSON(self):
        item = model_to_dict(self)
        item['Documento'] = self.prev_documento_id
        item['Fecha Creacion'] = self.prev_fecha_creacion
        item['Paquete'] = self.prev_paquete_id
        return item

# PREVISUALIZACION DEL LA VERSION
class PrevVersion(models.Model):
    prev_fecha = models.DateTimeField(verbose_name="Fecha Version", auto_now_add=True)
    prev_comentario = models.FileField(upload_to="proyecto/comentarios/", blank=True)
    prev_documento_fk = models.ForeignKey(Documento, on_delete=models.CASCADE) #relacion por defecto one to many en django
    prev_archivo = models.FileField(upload_to="proyecto/documentos/", blank=True)
    prev_revision = models.CharField(verbose_name="Emicion/Revision", max_length=1, default="B")
    prev_estado_cliente = models.IntegerField(choices=ESTADOS_CLIENTE, default=1, blank=True)
    prev_estado_contratista = models.IntegerField(choices=ESTADO_CONTRATISTA, default=1, blank=True)
    prev_owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creador")
    prev_paquete_fk = models.ForeignKey(PrevPaquete, on_delete=models.CASCADE, verbose_name="Paquete Preview")
    prev_valido = models.BooleanField(verbose_name="Valido", default=1) #1=VALIDO  0=ANULADO

    def __str__(self):
        return str(self.prev_documento_fk.Especialidad + self.prev_revision)
    
    def toJSON(self):
        item = model_to_dict(self)
        item['Documento'] = self.prev_documento_fk
        item['Fecha Creacion'] = self.prev_fecha
        item['Paquete'] = self.prev_paquete_id
        item['Revision'] = self.prev_revision
        item['Paquete'] = self.prev_paquete_fk
        return item

# FIN PREVISUALIZACION 