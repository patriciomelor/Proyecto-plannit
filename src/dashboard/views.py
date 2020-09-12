from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView, View
# Create your views here.


class RootView(RedirectView):
    pattern_name = 'account_login'

class IndexView(TemplateView):
    template_name = "index-base.html"

class EscritorioView(TemplateView):
    template_name = "administrador/Escritorio/dash.html"

class PdcView(TemplateView):
    template_name = "administrador/PaneldeCarga/pdc.html"
