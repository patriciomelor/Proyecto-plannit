from django.contrib.auth.models import User
from django.db import models
from configuracion.models import CausasNoCumplimiento, Restricciones

from panel_carga.models import Documento

# Create your models here.

class Tarea(models.Model):
    created_at = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1, related_name="autor", verbose_name="Autor", blank=True)
    documento = models.ForeignKey(Documento, related_name="task_document", on_delete=models.CASCADE, verbose_name="Documento")
    encargado = models.ForeignKey(User, related_name="responsable", on_delete=models.SET_DEFAULT, verbose_name="Encargado", default=1)
    restricciones = models.ForeignKey(Restricciones, on_delete=models.SET_NULL, related_name="task_restrictions", verbose_name="Restricciones", blank=True, null=True,)
    contidad_hh = models.IntegerField(verbose_name="Cantidad Horas Hombre")
    comentarios = models.TextField(verbose_name="Comentarios")
    estado = models.BooleanField(verbose_name="Estado", default=False, blank=True)
    archivo = models.FileField(verbose_name="Archivo", upload_to="tareas/documentos/", null=True, blank=True)
    plazo = models.DateField(verbose_name="Fecha Requerimiento")

    def __str__(self):
        return "Documento"+self.documento.Codigo_documento
class Respuesta(models.Model):
    STATES_TYPES = ((1,'Sin Evaluación'),(2,'Aprobado'), (3,'Rechazado'))

    contestado = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    tarea = models.ForeignKey(Tarea, related_name="task_answer", on_delete=models.CASCADE, verbose_name="Tarea")
    not_done = models.ForeignKey(CausasNoCumplimiento, on_delete=models.SET_NULL, related_name="answer_excuse", verbose_name="Causa no Cumplimiento", blank=True, null=True)
    contidad_hh = models.IntegerField(verbose_name="Cantidad Horas Hombre")
    comentarios = models.TextField(verbose_name="Comentarios", default="")
    archivo = models.FileField(verbose_name="Archivo", upload_to="respuestas/documentos/", null=True, blank=True)
    sent = models.BooleanField(verbose_name="Enviado", default=False, blank=True)
    estado = models.IntegerField(verbose_name="tipo de estado", choices=STATES_TYPES, default=1)
    motivo = models.TextField(verbose_name="Evaluación", default="", blank=True)