from django.db import models
from django.contrib.auth.models import User

ROLES = (
    ('','-----'),
    (1, 'Administrador'),
    (2, 'Revisor'),
    (3, 'Vizualizador'),
)

class Perfil(models.Model):
    usuario = models.OneToOneField(User, verbose_name="Usuario", on_delete=models.CASCADE)
    foto_de_perfil = models.ImageField(upload_to="perfil/foto/%Y/%m/%d", blank=True, null=True )
    rol_usuario = models.IntegerField(verbose_name='Rol de Usuario', choices=ROLES)
    empresa = models.CharField(verbose_name='Empresa', max_length=60)

    def __str__(self):
        return '{}+''+{}'.format(self.usuario.first_name, self.usuario.last_name)