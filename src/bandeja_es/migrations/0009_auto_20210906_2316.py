# Generated by Django 3.1.1 on 2021-09-07 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandeja_es', '0008_auto_20210502_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paquete',
            name='descripcion',
            field=models.TextField(blank=True, null=True, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='prevpaquete',
            name='prev_descripcion',
            field=models.TextField(blank=True, null=True, verbose_name='Descripción'),
        ),
    ]
