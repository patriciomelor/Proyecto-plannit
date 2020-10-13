from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic.base import ContextMixin
from panel_carga.models import Proyecto

class ProyectoSeleccionadoMixin(LoginRequiredMixin, ContextMixin):
    proyecto = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.session.get('proyecto', None):
            return HttpResponseRedirect(reverse_lazy('proyecto-select'))
        proyecto_id = request.session.get('proyecto')
        try:
            self.proyecto = Proyecto.objects.get(pk=proyecto_id)
        except Proyecto.DoesNotExist:
            HttpResponseRedirect(reverse_lazy('proyecto-crear'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proyecto'] = self.proyecto
        return context
    
    