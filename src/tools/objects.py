from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

class SuperUserViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        authorized = super(SuperUserViewMixin, self).dispatch(request, *args, **kwargs)
        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            return authorized

class StaffViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        authorized = super(SuperUserViewMixin, self).dispatch(request, *args, **kwargs)
        if not request.user.is_staff:
            raise PermissionDenied
        else:
            return authorized

def is_superuser_check(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def is_staff_check(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func