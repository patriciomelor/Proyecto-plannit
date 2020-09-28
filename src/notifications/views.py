from django.shortcuts import render
from django.views.generic import (ListView, DetailView)
from .models import Notificacion
# Create your views here.


class NotificacionList(ListView):
    model = Notificacion
    context_object_name = 'notificacion'
    template_name='notifications/main_box.html'

    def get_queryset(self, request):
        queryset = Notificacion.objects.filter(user=user).order_by('-date')

        return super().get_queryset(queryset)
    