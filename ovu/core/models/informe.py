from django.db import models


class Informe(models.Model):
    fecha = models.DateField()
    archivo = models.FileField(upload_to='uploads/')
    visible = models.BooleanField(default=True, help_text='¿Se puede visualizar este  informe?')
    url = models.URLField(default='#')

    def __str__(self):
        return f'Informe del {self.fecha.year}'
