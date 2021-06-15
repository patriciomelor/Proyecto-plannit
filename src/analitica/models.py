import json
from django.db import models
from panel_carga.models import Proyecto

# Create your models here.

class CurvasBase(models.Model):
    fecha_creacion = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, verbose_name="Proyecto")
    datos_lista = models.CharField(verbose_name="Datos Curva Base", max_length=1000)