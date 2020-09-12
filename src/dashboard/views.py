from django.shortcuts import render
from django.views.generic.base import TemplateView, RedirectView, View
# Create your views here.


class RootView(RedirectView):
    pattern_name = 'login'

class IndexView(TemplateView):
    template_name = "index-base.html"

<<<<<<< HEAD
=======
class EscritorioView(TemplateView):
    template_name = "administrador/Escritorio/dash.html"

class PdcView(TemplateView):
    template_name = "administrador/PaneldeCarga/pdc.html"
>>>>>>> 651f1d35d3e67fb0f4b38914c5797a436fc7f011
