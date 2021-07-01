from django.contrib.auth.models import User
from django.db import models
from configuracion.models import CausasNoCumplimiento, Restricciones

from panel_carga.models import Documento

# Create your models here.

class Tarea(models.Model):
    created_at = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    documento = models.ForeignKey(Documento, related_name="task_document", on_delete=models.CASCADE, verbose_name="Documento")
    encargado = models.ForeignKey(User, related_name="taks_responsable", on_delete=models.CASCADE, verbose_name="Encargado")
    restricciones = models.ForeignKey(Restricciones, on_delete=models.CASCADE, blank=True, null=True, related_name="task_restrictions", verbose_name="Restricciones")
    contidad_hh = models.IntegerField(verbose_name="Cantidad Horas Hombre")
    comentarios = models.TextField(verbose_name="Comentarios")
    estado = models.BooleanField(verbose_name="Estado", default=False, blank=True)
    archivo = models.FileField(verbose_name="Archivo", upload_to="respuestas/documentos/", null=True, blank=True)
    plazo = models.DateField(verbose_name="Fecha Requerimiento")

class Respuesta(models.Model):
    contestado = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    tarea = models.OneToOneField(Tarea, related_name="task_answer", on_delete=models.CASCADE, verbose_name="Tarea")
    not_done = models.ForeignKey(CausasNoCumplimiento, on_delete=models.CASCADE, related_name="answer_excuse", verbose_name="Causa no Cumplimiento", blank=True, null=True)
    contidad_hh = models.IntegerField(verbose_name="Cantidad Horas Hombre")
    comentarios = models.TextField(verbose_name="Comentarios")
    archivo = models.FileField(verbose_name="Archivo", upload_to="respuestas/documentos/", null=True, blank=True)
    sent = models.BooleanField(verbose_name="Enviado", default=False, blank=True)