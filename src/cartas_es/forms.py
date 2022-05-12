from cProfile import label
from django import forms
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField
from django.forms import BaseFormSet, widgets
from django.forms import (formset_factory, modelformset_factory)
from django.urls import (reverse_lazy, reverse)
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError

from crispy_forms.layout import Submit
from panel_carga.models import Documento
from django.contrib.auth.models import User

from .models import Carta
from panel_carga.views import ProyectoMixin

from panel_carga.choices import TYPES_REVISION
from panel_carga.models import Documento
#summernote
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

class CartaForm(forms.ModelForm):
    is_respuesta = forms.BooleanField(initial=False, help_text="Marcar solo para enviar como Carta de Respuesta", label="¿Enviar como Respuesta?")
    # cartas = forms.MultipleChoiceField(widget=forms.ModelMultipleChoiceField(queryset=))
    class Meta:
        model = Carta
        fields = ['destinatario', 'asunto', 'cuerpo', 'anexo']