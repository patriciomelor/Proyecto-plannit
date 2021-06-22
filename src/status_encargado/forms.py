from django import forms
from django.contrib.auth import models
from django.forms import BaseFormSet, fields, widgets
from django.forms import (formset_factory, modelformset_factory)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from .models import Tarea, Respuesta

from panel_carga.models import Documento


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        exclude = ["estado"]
        widgets = {
            'plazo': forms.DateInput(attrs={'type':'date'})
        }
class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = '__all__'