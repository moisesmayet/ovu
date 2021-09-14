import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_pandas.managers import DataFrameManager

from ovu.core.models import Indicador, Segregacion

ano_actual = datetime.date.today().year


class Corte(models.Model):
    PERIOD_CHOICES = [
        ('Bimestres', (
            ('b11', 'Bimestre 1-1'),
            ('b12', 'Bimestre 1-2'),
            ('b21', 'Bimestre 2-1'),
            ('b22', 'Bimestre 2-2'),
            ('b22', 'Bimestre 3-1'),
            ('b22', 'Bimestre 3-2'),
        )
         ),
        ('Trimestres', (
            ('t1', 'Trimestre 1'),
            ('t2', 'Trimestre 2'),
            ('t3', 'Trimestre 3'),
            ('t4', 'Trimestre 4'),
        )
         ),
        ('a', 'Anual'),
        ('Mensual', (
            ('en', 'Enero'),
            ('fe', 'Febrero'),
            ('ma', 'Marzo'),
            ('ab', 'Abril'),
            ('may', 'Mayo'),
            ('ju', 'Junio'),
            ('jul', 'Julio'),
            ('ag', 'Agosto'),
            ('se', 'Septiembre'),
            ('oc', 'Octubre'),
            ('no', 'Noviembre'),
            ('di', 'Diciembre'),
        )
         ),
    ]
    # corte_inicio = models.DateField(verbose_name='Fecha de inicio del corte')
    # corte_cierre = models.DateField(verbose_name='Fecha de cierre del corte')
    periodo = models.CharField(max_length=3, choices=PERIOD_CHOICES, default='b11')
    ano = models.PositiveSmallIntegerField(default=ano_actual, validators=[MaxValueValidator(ano_actual + 1),
                                                                           MinValueValidator(1995)],
                                           verbose_name='Año')
    visible = models.BooleanField(default=True, help_text='¿Se puede visualizar este corte?')
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(max_length=255, blank=True, null=True, verbose_name='Descripción')

    def save(self, *args, **kwargs):
        if self.nombre is None:
            self.nombre = f"{self.get_periodo_display()} {self.ano}"
        super(Corte, self).save()

    @property
    def to_str(self):
        return f"{self.ano}-{self.get_periodo_display()}"

    def __str__(self):
        return f"{self.ano}-{self.get_periodo_display()}"

    class Meta:
        ordering = ['ano', ]


class Dato(models.Model):
    valor = models.DecimalField(max_digits=11, decimal_places=3)

    segregacion = models.ForeignKey(Segregacion, on_delete=models.PROTECT, related_name='datos')
    indicador = models.ForeignKey(Indicador, on_delete=models.PROTECT, related_name='datos',
                                  limit_choices_to={'visible': True})
    corte = models.ForeignKey(Corte, on_delete=models.PROTECT, limit_choices_to={'visible': True})

    objects = DataFrameManager()

    def __str__(self):
        return f"{self.segregacion}-{self.corte}-{self.valor}"

    class Meta:
        unique_together = ['segregacion', 'corte', 'indicador']
