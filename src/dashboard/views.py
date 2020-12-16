from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import FormView
from panel_carga.views import ProyectoMixin
from django.contrib.auth.models import User


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


