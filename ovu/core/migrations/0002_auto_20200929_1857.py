# Generated by Django 3.0.10 on 2020-09-29 18:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='corte',
            name='ano',
            field=models.PositiveSmallIntegerField(default=2020, validators=[django.core.validators.MaxValueValidator(2021), django.core.validators.MinValueValidator(2019)], verbose_name='Año'),
        ),
        migrations.AlterField(
            model_name='corte',
            name='periodo',
            field=models.CharField(choices=[('Bimestres', (('b11', 'Bimestre 1-1'), ('b12', 'Bimestre 1-2'), ('b21', 'Bimestre 2-1'), ('b22', 'Bimestre 2-2'), ('b22', 'Bimestre 3-1'), ('b22', 'Bimestre 3-2'))), ('Trimestres', (('t1', 'Trimestre 1'), ('t2', 'Trimestre 2'), ('t3', 'Trimestre 3'), ('t4', 'Trimestre 4')))], default='b11', max_length=3),
        ),
    ]