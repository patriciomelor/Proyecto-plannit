# Generated by Django 3.1.1 on 2020-09-29 19:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Nombre del Proyecto')),
                ('fecha_inicio', models.DateTimeField(verbose_name='Fecha de Inicio')),
                ('fecha_temrino', models.DateTimeField(blank=True, verbose_name='Fecha de Termino')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('encargado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del Documento')),
                ('especialidad', models.CharField(max_length=100, verbose_name='Especialidad')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('num_documento', models.CharField(max_length=100, verbose_name='Número de Documento')),
                ('archivo', models.FileField(upload_to='proyecto/documentos/')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel_carga.proyecto')),
            ],
        ),
    ]