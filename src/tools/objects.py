from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

class SuperUserViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        authorized = super(SuperUserViewMixin, self).dispatch(request, *args, **kwargs)
        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            return authorized