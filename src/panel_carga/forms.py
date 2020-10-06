from django import forms
import django.forms.widgets
from .models import Proyecto, Documento, Revision

class ProyectoSelectForm(forms.Form):
    proyectos =  forms.ModelChoiceField(queryset=Proyecto.objects.all())

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = '__all__'

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = '__all__'

class RevisionForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = '__all__'