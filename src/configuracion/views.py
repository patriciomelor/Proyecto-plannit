from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import FormView
from panel_carga.views import ProyectoMixin
from django.contrib.auth.models import User

from .models import Perfil

# Create your views here.
class UsuarioView(ProyectoMixin, FormView):
    template_name = "administrador/Escritorio/create-user.html"
    form_class = CrearUsuario
    success_url = reverse_lazy('index')

    # def form_valid(self):
    #     data = form.cleaned_data
    #     user = User(


    #     )
    # def form_invalid(self):
    # def get(self, request, *args, **kwargs):
    # def post(self, request, *args, **kwargs):