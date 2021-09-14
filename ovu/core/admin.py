from django.contrib import admin

# Register your models here.
from django.template.defaultfilters import safe
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from ovu.core.models import Indicador, Componente, Algoritmo, FuenteInformacion, Termino, Ovu, \
    Objetivos, \
    Referencia, Segregacion, Corte, Dato, Informe

admin.site.site_header = 'Administración del OVU'


# ACTIONS
def make_invisible(self, request, queryset):
    rows_updated = queryset.update(visible=False)
    if rows_updated == 1:
        message_bit = "1 indicador se ha"
    else:
        message_bit = "%s indicadores se han" % rows_updated
    self.message_user(request, "%s actualizado a no visible satisfactoriamente." % message_bit)


def make_visible(self, request, queryset):
    rows_updated = queryset.update(visible=True)
    if rows_updated == 1:
        message_bit = "1 indicador se ha"
    else:
        message_bit = "%s indicadores se han" % rows_updated
    self.message_user(request, "%s actualizado a visible satisfactoriamente." % message_bit)


make_invisible.short_description = "Marcar como no visible"
make_visible.short_description = "Marcar como visible"


# RESOURCES
class ComponenteResource(resources.ModelResource):
    class Meta:
        model = Componente


class IndicadorResource(resources.ModelResource):
    class Meta:
        model = Indicador


class AlgoritmoResource(resources.ModelResource):
    class Meta:
        model = Algoritmo


class TerminoAlgoritmoResource(resources.ModelResource):
    class Meta:
        model = Termino


class FuenteInformacionAlgoritmoResource(resources.ModelResource):
    class Meta:
        model = FuenteInformacion


class ReferenciaResource(resources.ModelResource):
    class Meta:
        model = Referencia


class SegregacionResource(resources.ModelResource):
    class Meta:
        model = Segregacion


class DatoResource(resources.ModelResource):
    class Meta:
        model = Dato


# INLINES
class FuenteInformacionInline(admin.TabularInline):
    model = FuenteInformacion
    fields = ['fuente_informacion', 'web', 'registrado', ]
    extra = 0


class TerminoInline(admin.TabularInline):
    model = Termino
    extra = 0


class AlgoritmoInline(admin.TabularInline):
    model = Algoritmo
    extra = 0
    max_num = 1


class ReferenciaInline(admin.TabularInline):
    model = Referencia.indicador.through
    extra = 0
    verbose_name = "Referencia del Indicador"
    verbose_name_plural = "Referencias del Indicador"


class SegregacionInline(admin.TabularInline):
    model = Segregacion.indicador.through
    extra = 0
    max_num = 10


# ADMINS
@admin.register(Referencia)
class ReferenciaAdmin(ImportExportModelAdmin):
    resource_class = ReferenciaResource
    search_fields = ['institucion']


@admin.register(Componente)
class ComponenteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ComponenteResource
    list_display = ['codigo', 'nombre', '_indicadores', 'visible', ]
    search_fields = ['nombre', 'codigo', ]
    list_filter = ['visible', ]

    def _indicadores(self, obj):
        html = '<ul>'
        # html = '<img src="/{url}" width="{width}"height = {height} /> '
        for indicador in obj.indicadores.values_list('nombre'):
            print(html)
            html += ('<li>' + indicador[0] + '</li>')
        html += '</ul>'
        return format_html(html)


@admin.register(Indicador)
class IndicadorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = IndicadorResource
    list_per_page = 10
    list_display = ['id', 'codigo', 'nombre', 'cobertura_geografica', 'componente', 'visible', ]
    list_filter = ['visible', 'componente', 'cobertura_geografica', ]
    inlines = [AlgoritmoInline, FuenteInformacionInline, ReferenciaInline, SegregacionInline]
    search_fields = ['nombre', 'codigo', ]
    actions = [make_invisible, make_visible]


@admin.register(Algoritmo)
class AlgoritmoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = AlgoritmoResource
    inlines = [TerminoInline, ]
    list_display = ['_formula', 'unidad_medida', 'indicador', ]
    search_fields = ['indicador_nombre', ]

    def _formula(self, obj):
        return safe(obj.formula)


@admin.register(Termino)
class TerminoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TerminoAlgoritmoResource
    list_filter = ('tipo', 'algoritmo')
    inlines = [FuenteInformacionInline, ]
    list_display = ['tipo', 'variable', 'algoritmo', 'indicador', ]


@admin.register(FuenteInformacion)
class FuenteInformacionoAdmin(ImportExportModelAdmin):
    resource_class = FuenteInformacionAlgoritmoResource


@admin.register(Segregacion)
class SegregacionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = SegregacionResource
    list_display = ['id', 'parametro', 'parametro_opcional', '_indicadores', ]
    list_filter = ['indicador__codigo']
    search_fields = ['parametro', 'parametro_opcional', ]

    def _indicadores(self, obj):
        html = '<ul>'
        # html = '<img src="/{url}" width="{width}"height = {height} /> '
        for indicador in obj.indicador.values_list('nombre', 'codigo', ):
            print(html)
            html += ('<li>' + indicador[0] + f" ({indicador[1]})" + '</li>')
        html += '</ul>'
        return format_html(html)


@admin.register(Corte)
class CorteAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'periodo', 'ano', 'visible', ]
    list_filter = ['visible', ]
    search_fields = ['nombre']

    def _corte(self, obj):
        return obj


@admin.register(Dato)
class DatoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = DatoResource
    list_display = ['corte', 'segregacion', 'indicador', 'valor', ]
    list_filter = ['indicador__componente', 'indicador__codigo', 'corte', ]

    def _segregacion(self, obj):
        pass
        print(obj.segregacion.all())
        # html = '<ul>'
        # for s in obj.segregacion.all():
        #     print(html)
        #     html += ('<li>' + s.parametro + '</li>')
        # html += '</ul>'
        # return format_html(html)


@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ovu)
admin.site.register(Objetivos)
