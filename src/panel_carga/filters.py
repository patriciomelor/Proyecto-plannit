import django_filters
from django import forms
from .models import Documento
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class DocFilter(django_filters.FilterSet): 
    fecha_Emision_B = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'])
    fecha_Emision_0 = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'])

    class Meta:
        model=Documento
        fields = ['Especialidad', 'Descripcion', 'Codigo_documento','Tipo_Documento','Numero_documento_interno','fecha_Emision_B','fecha_Emision_0']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('Especilidad', css_class='form-control col-1 float-left',style="float:left;"),
                Column('Descipcion', css_class='form-control col-4 float-left'),
                Column('Codigo_documento',css_class="form-control col-4 float-left"),                
                css_class='col-12'
            ),
            Row(
                Column('Tipo_Documento', css_class='form-control col-3 mb-0 float-left'),
                Column('Numero_documento_interno', css_class='form-control col-3 mb-0 float-left'),
                Column('fecha_Emision_B', css_class='form-control col-3 mb-0 float-left'),
                Column('fecha_Emision_0', css_class='form-control col-3 mb-0 float-left'),

                css_class='col-12'
            ),
            'check_me_out',
            Submit('submit', 'filtrar')
        )