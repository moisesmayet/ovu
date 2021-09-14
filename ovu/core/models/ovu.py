from django.db import models


class Ovu(models.Model):
    nombre = models.CharField(max_length=15, null=True, blank=True)
    definicion = models.TextField(max_length=255)


class Objetivos(models.Model):
    objetivo = models.CharField(max_length=100)

    ovu = models.ForeignKey(Ovu, on_delete=models.PROTECT)
