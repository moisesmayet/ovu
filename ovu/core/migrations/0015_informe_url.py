# Generated by Django 3.1.8 on 2021-05-27 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_informe_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='informe',
            name='url',
            field=models.URLField(default='#'),
        ),
    ]