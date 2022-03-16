from django.shortcuts import render

# Create your views here.

from tools.objects import AdminViewMixin, SuperuserViewMixin, VisualizadorViewMixin
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView,View)
from django.db import IntegrityError


from notifications.emails import send_email
from panel_carga.views import ProyectoMixin
from panel_carga.models import Documento, Proyecto
from django.views.decorators.csrf import csrf_exempt
# from .models

class CartasIndex(ProyectoMixin, View):
    pass

class CreateCarta(ProyectoMixin, CreateView):
    pass

class UpdateCarta(ProyectoMixin, UpdateView):
    pass

class DeleteCarta(ProyectoMixin, AdminViewMixin, DeleteView):
    pass

class CreateCartaRespuesta(ProyectoMixin, CreateView):
    pass

class UpdateCartaRespuesta(ProyectoMixin, UpdateView):
    pass

class DeleteCartaRespuesta(ProyectoMixin, DeleteView):
    pass
