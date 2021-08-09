from django.views.generic.edit import FormView
from panel_carga.views import ProyectoMixin
from django.shortcuts import render
from django.views.generic import (ListView, DetailView)
from .models import Notificacion
# Create your views here.

class EmailBaseView(ProyectoMixin, FormView):
    pass

class NotificacionList(ProyectoMixin, ListView):
    model = Notificacion
    context_object_name = 'notificaciones'
    template_name='notifications/main_box.html'

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user).order_by('-date')
    
class NotificationDetail(ProyectoMixin, DetailView):
    model = Notificacion
    context_object_name = 'notificacion'
    template_name = 'notifications/detail-notification.html'

    def get(self, request, *args, **kwargs):
        noti = self.get_object()
        noti.is_seen = True
        noti.save()
        return super(NotificationDetail, self).get(request, *args, **kwargs)