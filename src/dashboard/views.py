from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import FormView
from panel_carga.views import ProyectoMixin

from .models import Perfil
from .forms import CrearUsuario

# Create your views here.

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

class RootView(RedirectView):
    pattern_name = 'account_login'

class IndexView(ProyectoMixin, TemplateView):
    template_name = "index-base.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proyecto"] = self.proyecto
        return context
    

class EscritorioView(ProyectoMixin, TemplateView):
    template_name = "administrador/Escritorio/dash.html"

class UsuarioView(ProyectoMixin, FormView):
    template_name = "administrador/Escritorio/create-user.html"
    form_class = CrearUsuario
    success_url = reverse_lazy('index')

    # def form_valid(self):
    # def form_invalid(self):
    # def get(self, request, *args, **kwargs):
    # def post(self, request, *args, **kwargs):
