from django.shortcuts import render
from django.views.generic.base import TemplateView
# Create your views here.

class IndexView(TemplateView):
    template_name = "index-base.html"

class EscritorioView(TemplateView):
    template_name = "administrador/Escritorio/dash.html"

class PdcView(TemplateView):
    template_name = "administrador/PaneldeCarga/pdc.html"