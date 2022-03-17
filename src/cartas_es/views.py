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
from .forms import CartaForm
from .models import Carta, CartaRespuesta
from itertools import chain 


class CartasRecibidos(ProyectoMixin, ListView):
    template_name = 'cartas_es/cartas_recibidos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cartas = Carta.objects.filter(proyecto=self.proyecto, destinatario=self.request.user)
        cartas_respuesta = CartaRespuesta.objects.filter(proyecto=self.proyecto, destinatario=self.request.user)
        #querysets unidas y ordenadas por fecha
        result_list = sorted(chain(cartas, cartas_respuesta), key= lambda instance: instance.fecha_creacion)
        context["cartas"] = result_list
        return context

class CartasEnviadas(ProyectoMixin, ListView):
    template_name = 'cartas_es/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cartas = Carta.objects.filter(proyecto=self.proyecto, autor=self.request.user)
        cartas_respuesta = CartaRespuesta.objects.filter(proyecto=self.proyecto, autor=self.request.user)
        #querysets unidas y ordenadas por fecha
        result_list = sorted(chain(cartas, cartas_respuesta), key= lambda instance: instance.fecha_creacion)
        context["cartas"] = result_list
        return context

class CreateCarta(ProyectoMixin, CreateView):
    model = Carta
    form_class = CartaForm


class CartaDetail(ProyectoMixin, DetailView):
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
