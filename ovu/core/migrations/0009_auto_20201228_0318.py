# Generated by Django 3.0.10 on 2020-12-28 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20201228_0304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicador',
            name='definicion',
            field=models.TextField(blank=True, max_length=1024, null=True, verbose_name='Definición'),
        ),
        migrations.AlterField(
            model_name='indicador',
            name='descripcion',
            field=models.TextField(blank=True, max_length=1024, null=True, verbose_name='Descripción'),
        ),
    ]