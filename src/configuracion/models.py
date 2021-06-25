from panel_carga.models import Proyecto
from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from .roles import *

def get_full_name(self):
    return str(self.first_name+" "+self.last_name)

User.add_to_class("__str__", get_full_name)

class Perfil(models.Model):
    usuario = models.OneToOneField(User, verbose_name="Usuario", on_delete=models.CASCADE)
    foto_de_perfil = models.ImageField(upload_to="perfil/foto/%Y/%m/%d", blank=True, null=True )
    rol_usuario = models.IntegerField(verbose_name='Rol de Usuario', choices=ROLES)
    empresa = models.CharField(verbose_name='Empresa', max_length=60)
    client = models.BooleanField(verbose_name='Es cliente', default=True)

    def __str__(self):
        return str(self.get_rol_usuario_display())
        

class Restricciones(models.Model):
    nombre = models.CharField(verbose_name="Nombre", max_length=30)
    created_at = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="proyect_restrictions", verbose_name="Proyecto")
    def __str__(self):
        return self.nombre

class CausasNoCumplimiento(models.Model):
    nombre = models.CharField(verbose_name="Nombre", max_length=30)
    created_at = models.DateTimeField(verbose_name="Fecha Creación", auto_now_add=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="proyect_no_complete", verbose_name="Proyecto")

    def __str__(self):
        return self.nombre