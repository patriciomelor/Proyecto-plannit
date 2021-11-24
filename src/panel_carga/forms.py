from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet
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
        exclude = ["umbral_documento_aprobado", "umbral_documento_atrasado", "umbral_revision_documento", "umbral_desviacion_porcentual", "participantes"]
        widgets = {
            'fecha_inicio':forms.TextInput(attrs={'type': 'date'}),
            'fecha_termino':forms.TextInput(attrs={'type': 'date'}),
            'descripcion':forms.Textarea(attrs={'row':'5','style':'height:100px;'}),
            # 'participantes': forms.CheckboxSelectMultiple
        }
        labels = {
            'codigo':'Código del Proyecto',
            'fecha_termino':'Fecha de Término',
            # 'umbral_desviacion_porcentual':'Umbral para Desviación Porcentual del Proyecto'

        }

class DocumentoForm(forms.ModelForm):  

    class Meta:
        model = Documento
        exclude = ['tipo','owner','emision','proyecto', 'ultima_edicion', 'archivo', 'Numero_documento_interno', 'Codigo_documento']
        widgets = {
            'fecha_Emision_B':forms.TextInput(attrs={'type': 'datetime','class':'form-control datepicker','placeholder':'DD/MM/YYYY'}),
            'fecha_Emision_0':forms.TextInput(attrs={'type': 'datetime','class':'form-control datepicker','placeholder':'DD/MM/YYYY'}),
        }
        labels = {
            'Descripcion':'Descripción',
            'Tipo_Documento':'Tipo',
            'fecha_Emision_B':'Fecha Emisión B',
            'fecha_Emision_0':'Fecha Emisión 0'
        }
    def __init__(self, **kwargs):
        super(DocumentoForm, self).__init__(**kwargs)
        instance = getattr(self, 'instance', None)
        # self.fields['Codigo_documento'].widget.attrs['disabled'] = 'disabled'

class RevisionForm(forms.ModelForm):
    
    class Meta:
        model = Revision
        fields = '__all__'


class BaseDocFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseDocFormSet, self).__init__(*args, **kwargs)
        self.documentos = self.form_kwargs["documentos"]
        self.queryset = Documento.objects.filter(pk__in=self.documentos)

DocEditFormset = modelformset_factory(Documento, form= DocumentoForm, extra=0)