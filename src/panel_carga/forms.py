from django import forms
import django.forms.widgets
from .models import Proyecto, Documento, Revision
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ProyectoSelectForm(forms.Form):
    proyectos =  forms.ModelChoiceField(queryset=Proyecto.objects.all())

class ProyectoForm(forms.ModelForm):
    nombre = forms.CharField( max_length=50, required=True)
    fecha_inicio = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])
    class Meta:
        model = Proyecto
        fields = ['encargado']

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = '__all__'

class RevisionForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = '__all__'