# Generated by Django 3.1.1 on 2021-10-20 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bandeja_es', '0017_auto_20211019_1939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paquete',
            name='comentario3',
        ),
        migrations.RemoveField(
            model_name='paquete',
            name='comentario4',
        ),
        migrations.RemoveField(
            model_name='prevpaquete',
            name='prev_comentario3',
        ),
        migrations.RemoveField(
            model_name='prevpaquete',
            name='prev_comentario4',
        ),
    ]