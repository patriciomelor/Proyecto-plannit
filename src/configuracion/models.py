from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, verbose_name="Usuario", on_delete=models.CASCADE)
    foto_de_perfil = models.ImageField(upload_to="perfil/foto/%Y/%m/%d", blank=True, null=True )
    administrador = models.BooleanField(default=0, verbose_name="Administrador")
    revisor = models.BooleanField(default=0, verbose_name="Revisor")
    visualizador = models.BooleanField(default=0, verbose_name="Visualizador")

    def __str__(self):
        return '{}+''+{}'.format(self.usuario.first_name, self.usuario.last_name)