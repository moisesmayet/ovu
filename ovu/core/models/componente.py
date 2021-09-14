from django.db import models
from tinymce.models import HTMLField

from config.settings.base import STATIC_URL


class Componente(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=5, verbose_name='Código')
    descripcion = HTMLField(blank=True, null=True, verbose_name='Descripción')

    eliminable = models.BooleanField(default=True, editable=False)
    visible = models.BooleanField(default=True, help_text='¿Se puede visualizar este componente?')

    def __str__(self):
        return f'{self.codigo} {self.nombre}'

    def total_componentes(self=None): return Componente.objects.count()

    @property
    def total_indicadores(self):
        return self.indicadores.count()

    @property
    def indicadores_list(self):
        return self.indicadores.filter(visible=True).all()

    @property
    def image(self):
        url_base = f"{STATIC_URL}images/componentes/"
        if self.codigo in [f"C{i}" for i in range(13)]:
            return url_base + self.codigo + '.svg'
        return url_base + 'C0' + '.svg'

    @property
    def icon(self):
        url_base = f"{STATIC_URL}images/componentes/iconos/"
        if self.codigo in [f"C{i}" for i in range(13)]:
            return url_base + self.codigo + '.svg'
        return url_base + 'C0' + '.svg'


    class Meta:
        ordering = ['pk']

    # def delete(self):
    #     if not self.eliminable:
    #         print(f'No se puede eliminar el componente {self.codigo} {self.nombre}')
    #         return f'No se puede eliminar el componente {self.codigo} {self.nombre}'
    #     else:
    #         super().delete()

    # def save(self, *args, **kwargs):
    #     self.nombre = f"C{self.-1}"
    #     super().save()
