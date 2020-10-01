from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DeleteView
from django.views.generic.base import ContextMixin

# class ProyectoSeleccionadoMixin(LoginRequiredMixin, ContextMixin):
#     proyecto = None
    
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
#         if not request.sessions.get('proyecto', None):
#             return HttpResponseRedirect(reverse_lazy('proyecto-select'))
#         return super().dispatch(request, *args, **kwargs)
    