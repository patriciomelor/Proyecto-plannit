from django import forms
import django.forms.widgets
from .models import Proyecto, Documento, Revision
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



class UploadFileForm(forms.Form):
    importfile = forms.FileField()

class ProyectoSelectForm(forms.Form):
    proyectos = forms.ModelChoiceField(queryset=None)
    
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('proyectos')
        super(ProyectoSelectForm, self).__init__(*args, **kwargs)
        self.fields['proyectos'].queryset = qs

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = '__all__'
        widgets = {
            'fecha_inicio':forms.TextInput(attrs={'type': 'date'}),
            'fecha_termino':forms.TextInput(attrs={'type': 'date'}),
            'descripcion':forms.Textarea(attrs={'row':'5','style':'height:100px;'}),
            # 'participantes': forms.CheckboxSelectMultiple
        }
        labels = {
            'codigo':'Código del Proyecto',
            'fecha_termino':'Fecha de Término',
            'umbral_desviacion_porcentual':'Umbral para Desviación Porcentual del Proyecto'

        }

class DocumentoForm(forms.ModelForm):  

    class Meta:
        model = Documento
        exclude = ['tipo','owner','emision','proyecto', 'ultima_edicion', 'archivo', 'Numero_documento_interno']
        widgets = {
            'fecha_Emision_B':forms.TextInput(attrs={'type': 'date'}),
            'fecha_Emision_0':forms.TextInput(attrs={'type': 'date'}),
        }
        labels = {
            'Descripcion':'Descripción',
            'Codigo_documento':'Código',
            'Tipo_Documento':'Tipo',
            'fecha_Emision_B':'Fecha Emisión B',
            'fecha_Emision_0':'Fecha Emisión 0'
        }

class RevisionForm(forms.ModelForm):
    
    class Meta:
        model = Revision
        fields = '__all__'