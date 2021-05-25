from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

class SuperuserViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        authorized = super(SuperuserViewMixin, self).dispatch(request, *args, **kwargs)
        if request.user.is_superuser:
            return authorized
        else:
            raise PermissionDenied
            
class AdminViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        authorized = super(AdminViewMixin, self).dispatch(request, *args, **kwargs)
        if request.user.is_superuser:
            return authorized
        rol = request.user.perfil.rol_usuario
        if rol == 1 or rol == 4:
            return authorized
        else:
            raise PermissionDenied

def is_admin_check(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.perfil.rol_usuario == 1 or request.user.perfil.rol_usuario == 4:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper_func

def is_superuser_check(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func