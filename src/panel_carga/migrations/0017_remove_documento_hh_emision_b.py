# Generated by Django 3.1.1 on 2022-01-21 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panel_carga', '0016_auto_20220114_1235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documento',
            name='hh_emision_B',
        ),
    ]