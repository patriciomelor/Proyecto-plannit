from django.shortcuts import render
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView, View
from panel_carga.views import ProyectoMixin

# from .models import 
# Create your views here.

class IndexView(ProyectoMixin, TemplateView):
    template_name = 'bandeja_es/baes.html'