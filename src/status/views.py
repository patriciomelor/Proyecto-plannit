from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from django.contrib import messages

from .filters import DocFilter
from panel_carga.models import Documento
from bandeja_es.models import Version, Paquete
# Create your views here

class StatusIndex(ProyectoMixin, TemplateView):
    template_name = 'status/index.html'