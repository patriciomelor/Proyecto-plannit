import json
from django.db import models
from django.db.models.fields import CharField
from panel_carga.models import Proyecto
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class CurvasBase(models.Model):
    fecha_creacion = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, verbose_name="Proyecto")
    datos_lista = ArrayField(base_field=models.CharField(max_length=1000, blank=True))

    def get_list(self, list):
        self.datos_lista = json.dumps(list)

    def get_lista(self):
        datos = json.loads(self.datos_lista)
        return datos

class CurvasBaseHH(models.Model):
    fecha_creacion = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, verbose_name="Proyecto")
    datos_lista = ArrayField(base_field=models.CharField(max_length=1000, blank=True))

    def get_list(self, list):
        self.datos_lista = json.dumps(list)

    def get_lista(self):
        datos = json.loads(self.datos_lista)
        return datos

class CurvasBaseValor(models.Model):
    fecha_creacion = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, verbose_name="Proyecto")
    datos_lista = ArrayField(base_field=models.CharField(max_length=1000, blank=True))

    def get_list(self, list):
        self.datos_lista = json.dumps(list)

    def get_lista(self):
        datos = json.loads(self.datos_lista)
        return datos