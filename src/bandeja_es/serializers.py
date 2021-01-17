from rest_framework import serializers
from .models import Version

class PrevVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = ['prev_documento_fk', 'prev_revision', 'prev_archivo','prev_comentario' ,'prev_estado_cliente', 'prev_estado_contratista', 'prev_owner']
