# Generated by Django 3.1.8 on 2021-05-25 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20210525_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='informe',
            name='visible',
            field=models.BooleanField(default=True, help_text='¿Se puede visualizar este  informe?'),
        ),
    ]