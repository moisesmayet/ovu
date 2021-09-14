import itertools

import pandas as pd
import numpy as np

import plotly.express as px
from django.core.exceptions import EmptyResultSet
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import safe, striptags
from django.utils.timezone import now as today
from plotly.offline import plot
from tinymce.models import HTMLField

import plotly.io as pio

pio.renderers.default = 'browser'

from ovu.core.configuraciones import SEGREGACIONES_PROFUNDIDAD_TRES, NO_GRAFICAS, LABELS, \
    TABLA_PORCENTUAL, TABLAS_LINEAL, TABLAS_PROMEDIO, SEGREGACIONES_PROFUNDIDAD_TRES_TABS, TABLA_SIN_SUMATORIA, \
    TABA_SUMATORIA_SOLO_VERTICAL, NO_BARS, TOTALES_BARS, PROMEDIOS_BARS, PIE, SUNBURTS, PREGRADO, GRADO, POSTGRADO, \
    TABS, TABS_SUMATORIA_SOLO_VERTICAL_TABS, EXEPCIONES_DECIMALES, TABS_PROMEDIO_TABS
from ovu.core.models import Componente


def switch_indicador_table_size(indicador):
    if indicador in ['CES.01', 'CES.03', 'CES.04', 'CES.05', 'CES.06', 'CES.07', 'OA.01', 'OA.02', 'OA.03', 'OA.04',
                     'DU.04', ]:
        return 10
    return 5


class Indicador(models.Model):
    COBERTURA_CHOICES = [
        ('Na', 'Nacional'),
        ('Inter', 'Internacional'),
    ]

    PERIODICIDAD_CHOICES = [
        ('M', 'Mensual'),
        ('BM', 'Bimensual'),
        ('BT', 'Bimestral'),
        ('A', 'Anual'),
        ('CU', 'Cuatrimestral'),
        ('TR', 'Trimestral'),
        ('CT', 'Cuatrimestral/Trimestral'),
        ('P', 'Pendiente'),
    ]

    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=10)
    descripcion = models.TextField(max_length=1024, blank=True, null=True, verbose_name='Descripción')
    definicion = models.TextField(max_length=1024, blank=True, null=True, verbose_name='Definición')
    eliminable = models.BooleanField(default=False, help_text='¿Se puede eliminar este indicador?')
    visible = models.BooleanField(default=False, help_text='¿Se puede visualizar este indicador?')
    cobertura_geografica = models.CharField(max_length=5, choices=COBERTURA_CHOICES, default='Na',
                                            verbose_name='Cobertura geográfica')
    periodicidad = models.CharField(max_length=2, choices=PERIODICIDAD_CHOICES, default='A')
    # fecha_difusion = models.DateField(blank=True, null=True, verbose_name='Fecha de difusión')
    # periodo_referencia_inicia = models.DateField(blank=True, null=True, )
    # periodo_referencia_termina = models.DateField(blank=True, null=True, )
    lectura = models.TextField(default='Pendiente la información', verbose_name='Lectura del Indicador')
    observaciones = HTMLField(blank=True, null=True, )

    componente = models.ForeignKey(Componente, on_delete=models.PROTECT, related_name='indicadores',
                                   related_query_name='indicador')

    # tiene_datos = False

    def save(self, *args, **kwargs):
        if self.componente.eliminable:
            self.componente.eliminable = False
            self.componente.save()
        super().save()

    def total_indicadores_visibles(self=None):
        return Indicador.objects.filter(visible=True).count()

    def listado_datos(self, para_descargar=False):
        check_list = list(
            itertools.chain(SEGREGACIONES_PROFUNDIDAD_TRES, SEGREGACIONES_PROFUNDIDAD_TRES_TABS, TABS_PROMEDIO_TABS))

        if para_descargar:
            if self.codigo in check_list:
                return self.datos.values('segregacion__parametro', 'segregacion__parametro_opcional', 'valor',
                                         'corte__nombre')
            return self.datos.values('segregacion__parametro', 'valor', 'corte__nombre')

        if self.codigo in check_list:
            return self.datos.values('segregacion__parametro', 'segregacion__parametro_opcional', 'valor',
                                     'corte__nombre')
            # return self.datos.values('segregacion__parametro', 'segregacion__parametro_opcional', 'valor',
            #                          'corte__nombre')[:switch_indicador_table_size(self.codigo)]
        return self.datos.values('segregacion__parametro', 'valor', 'corte__nombre')

    def con_graficas(self):
        if self.codigo not in NO_GRAFICAS:
            return True
        return False

    @property
    def indicadores_porcentuales(self):
        return TABLA_PORCENTUAL

    @property
    def tiene_datos(self):
        return True if self.datos.all().count() > 0 else False

    @property
    def segregaciones(self):
        if self.codigo in SEGREGACIONES_PROFUNDIDAD_TRES:
            segregaciones_total = list(self.segregacion.values_list('parametro', flat=True))
            segregaciones_total.append('Total')
            return segregaciones_total
        return self.segregacion.all()

    def datos_table_parametro_opcional(self, pdt: pd.DataFrame, programa=''):
        pd.set_option("display.max_rows", None, "display.max_columns", None, )
        pd.set_option('precision', 2)
        pd.options.display.float_format = '{:.1f}'.format

        if self.codigo in ['CES.02', 'OA.021', 'OA.02', 'SU.13', 'RH.04', 'RH.03', 'RH.05', 'RH.08', 'RH.09',
                           'IP.01', 'IP.03', ]:
            pdt['corte__nombre'] = [x.replace('Anual', '') for x in pdt['corte__nombre']]
            pdt['valor'] = pd.to_numeric(pdt['valor'])

            pivot = pdt.pivot_table(index=['segregacion__parametro_opcional'],
                                    columns=['corte__nombre', 'segregacion__parametro'], values='valor',
                                    aggfunc='sum', margins=True, fill_value=0)

        else:
            pivot = pdt.pivot_table(index=['segregacion__parametro_opcional'],
                                    columns=['corte__nombre', 'segregacion__parametro'], values='valor',
                                    aggfunc='sum', margins=True, fill_value=0)

        pivot.index.names = [LABELS.get(self.codigo, '')]
        pivot.columns.names = ['' for name in pivot.columns.names]
        # pivot.index.names = ['']

        pivot.rename(columns={'All': 'Total'}, index={'All': 'Total'}, inplace=True)

        # pivot.rename(columns={'All': 'Total', 'names.corte__nombre': 'Serr'},
        #              index={'All': 'Total', 'segregacion__parametro_opcional': 'sdsds'}, inplace=True)
        # return pivot.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])
        return pivot

    def datos_table_parametro_opcional_tabs(self, pdt: pd.DataFrame):
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        nan_value = float("NaN")

        import re
        # df_grado = pdt[pdt['segregacion__parametro_opcional'].str.contains('|'.join(GRADO))]
        # df_pregrado = pdt[pdt['segregacion__parametro_opcional'].str.contains('|'.join(PREGRADO))]
        # df_postgrado = pdt[pdt['segregacion__parametro_opcional'].str.contains('|'.join(POSTGRADO))]
        df_grado = pdt[pdt['segregacion__parametro_opcional'].str.strip().isin(GRADO)]
        df_pregrado = pdt[pdt['segregacion__parametro_opcional'].str.contains('|'.join(PREGRADO))]
        df_postgrado = pdt[pdt['segregacion__parametro_opcional'].str.contains('|'.join(POSTGRADO))]

        # GRADO
        if not df_grado.empty:
            df_grado['corte__nombre'] = [x.replace('Anual', '') for x in df_grado['corte__nombre']]
            df_grado['valor'] = df_grado['valor'].astype('float64')

            pivot_grado = df_grado.pivot_table(index=['segregacion__parametro_opcional'],
                                               columns=['corte__nombre', 'segregacion__parametro'], values='valor',
                                               fill_value=0)
            pivot_grado.loc['Total Grado'] = pivot_grado.sum()

            # pivot_grado.style.background_gradient(cmap='coolwarm')
        else:
            pivot_grado = pd.DataFrame([])
        # PREGRADO
        if not df_pregrado.empty:
            df_pregrado['corte__nombre'] = [x.replace('Anual', '') for x in df_pregrado['corte__nombre']]
            df_pregrado['valor'] = df_pregrado['valor'].astype('float64')
            pivot_pregrado = df_pregrado.pivot_table(index=['segregacion__parametro_opcional'],
                                                     columns=['corte__nombre', 'segregacion__parametro'],
                                                     values='valor',
                                                     fill_value=0)
            pivot_pregrado.loc['Total Pregrado'] = pivot_pregrado.sum()
        else:
            pivot_pregrado = pd.DataFrame([])
        # # POSTGRADO
        if not df_postgrado.empty:
            df_postgrado['corte__nombre'] = [x.replace('Anual', '') for x in df_postgrado['corte__nombre']]
            df_postgrado['valor'] = df_postgrado['valor'].astype('float64')
            pivot_postgrado = df_postgrado.pivot_table(index=['segregacion__parametro_opcional'],
                                                       columns=['corte__nombre', 'segregacion__parametro'],
                                                       values='valor', fill_value=0)
            pivot_postgrado.loc['Total Postgrado'] = pivot_postgrado.sum()
        else:
            pivot_postgrado = pd.DataFrame([])

        try:
            pivot = pivot_pregrado.append(pivot_grado)
        except:
            pass

        try:
            pivot = pivot_pregrado.append(pivot_grado).append(pivot_postgrado)
        except:
            pass

        try:
            pivot.append(pivot_postgrado)
        except:
            pass

        pivot.index.names = [LABELS.get(self.codigo, '')]
        pivot.columns.names = ['' for name in pivot.columns.names]

        return pivot

    @property
    def datos_tabla_porcentual(self):
        df = pd.DataFrame(self.listado_datos())

        df['percent'] = (df['valor'] / df['valor'].sum()) * 100
        df['percent'] = df['percent'].astype('float64')

        if self.codigo in TABLA_PORCENTUAL:
            pvt = df.pivot_table(index='segregacion__parametro', columns='corte__nombre', values='percent',
                                 aggfunc='sum', margins=True, fill_value=0)
        else:
            pvt = df.pivot_table(index=['segregacion__parametro_opcional'],
                                 columns=['corte__nombre', 'segregacion__parametro'], values='percent',
                                 aggfunc='sum', margins=True, fill_value=0)

        pvt.index.names = [LABELS.get(self.codigo, '')]
        pvt.columns.names = ['' for name in pvt.columns.names]
        pvt.rename(columns={'All': 'Total'}, index={'All': 'Total'}, inplace=True)
        pvt.rename(columns={'All': 'Total'}, index={'All': 'Total'}, inplace=True)

        # pvt.style.hide_index().set_caption('Colormaps, with a caption.')

        return pvt.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])

    def pivot_tabla_lineal(self, df):
        df_t = df
        df_t['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        df_t['corte__nombre'] = [x.replace('Anual', '') for x in df_t['corte__nombre']]

        df_t.index.names = [LABELS.get(self.codigo, '')]
        # df_pivot.columns.names = ['']
        # df_pivot.index.names = ['']

        return pd.pivot_table(df_t, index='segregacion__parametro', columns='corte__nombre', values='valor')

    def pivot_tabla_sumatoria(self, df, con_sumatoria=True, sumatoria_solo_vertical=False):
        df_t = df
        df_t['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        df_t['corte__nombre'] = [x.replace('Anual', '') for x in df_t['corte__nombre']]

        if con_sumatoria and sumatoria_solo_vertical:
            pivot = df_t.pivot(index='segregacion__parametro', columns='corte__nombre', values='valor')
            pivot.loc['Total'] = pivot.sum()
            # print(df)
        elif con_sumatoria:
            # df_t.rename(columns={'All': 'Total'}, index={'All': 'Total'}, inplace=True)
            pivot = df_t.pivot_table(index='segregacion__parametro', columns='corte__nombre', values='valor',
                                     aggfunc='sum', margins=True, fill_value=0)
            pivot.rename(columns={'All': 'Total'}, index={'All': 'Total'}, inplace=True)
        else:
            df_t['valor'] = df_t['valor'].astype('float64')
            pivot = df_t.pivot(index='segregacion__parametro', columns='corte__nombre', values='valor')

        pivot.index.names = [LABELS.get(self.codigo, '')]
        pivot.columns.names = ['' for name in pivot.columns.names]

        return pivot

    def pivot_tabla_promedio(self, df):
        df_t = df
        df_t['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        df_t['corte__nombre'] = [x.replace('Anual', '') for x in df_t['corte__nombre']]

        if self.codigo in TABS_PROMEDIO_TABS:
            df_t['corte__nombre'] = [x.replace('Anual', '') for x in df_t['corte__nombre']]

            pivot = df_t.pivot_table(index=['segregacion__parametro_opcional'],
                                     columns=['corte__nombre', 'segregacion__parametro'], values='valor',
                                     fill_value=0)
            pivot.loc['Promedio'] = pivot.mean()
            pivot.index.names = [LABELS.get(self.codigo, '')]
            pivot.columns.names = ['' for name in pivot.columns.names]
            return pivot

        pivot = df_t.pivot_table(index='segregacion__parametro', columns='corte__nombre', values='valor', fill_value=0)
        pivot.loc['Promedio'] = pivot.mean()

        pivot.index.names = [LABELS.get(self.codigo, '')]
        pivot.columns.names = ['' for name in pivot.columns.names]

        return pivot

    def anos_tabs(self, anos):
        return anos

    @property
    def datos_html_table(self):
        listado_datos = None
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        pd.set_option('precision', 0)
        # pd.options.display.float_format = '{:.2f}'.format

        if self.codigo in EXEPCIONES_DECIMALES:
            pd.set_option('precision', 1)
            # pd.set_option('precision', 3)
        elif self.codigo == 'DU.04':
            pd.set_option('precision', 1)
            # pd.options.display.float_format = '{:.3f}'.format

        try:
            df = pd.DataFrame(self.listado_datos())

            if self.codigo in SEGREGACIONES_PROFUNDIDAD_TRES:
                df_pivot = self.datos_table_parametro_opcional(pdt=df)
            elif self.codigo in TABLAS_LINEAL:
                df_pivot = self.pivot_tabla_lineal(df)

                df_pivot.index.names = [LABELS.get(self.codigo, '')]
                df_pivot.columns.names = ['']
            elif self.codigo in TABLAS_PROMEDIO:
                df_pivot = self.pivot_tabla_promedio(df)

            elif self.codigo in TABS:
                pd.set_option("display.max_rows", None, "display.max_columns", None)

                lista_anos = sorted(set(df.corte__nombre.tolist()))
                tablas = []
                self.anos_tabs(list(lista_anos))

                for corte in lista_anos:
                    # para postgrado
                    # df_pivot = self.datos_table_parametro_opcional_tabs(pdt=df[df.corte__nombre == corte])
                    if self.codigo in ['DU.04', 'DU.05', ]:
                        df_pivot = self.datos_table_parametro_opcional_tabs(pdt=df[df.corte__nombre == corte])
                    else:
                        if self.codigo in TABS_SUMATORIA_SOLO_VERTICAL_TABS:
                            df_pivot = self.pivot_tabla_sumatoria(df[df.corte__nombre == corte],
                                                                  sumatoria_solo_vertical=True)
                        if self.codigo in TABS_PROMEDIO_TABS:
                            print(df)
                            print(60 * '-')
                            df_pivot = self.pivot_tabla_promedio(df[df.corte__nombre == corte])
                        elif self.codigo in SEGREGACIONES_PROFUNDIDAD_TRES_TABS:
                            df_pivot = self.datos_table_parametro_opcional(pdt=df[df.corte__nombre == corte])
                        else:
                            df_pivot = self.datos_table_parametro_opcional(df[df.corte__nombre == corte])
                    tablas.append(df_pivot.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"],
                                                   na_rep='0'))

                return tablas, list(lista_anos)

            else:
                if self.codigo not in TABLA_SIN_SUMATORIA:
                    if self.codigo in TABA_SUMATORIA_SOLO_VERTICAL:
                        df_pivot = self.pivot_tabla_sumatoria(df, sumatoria_solo_vertical=True)
                    else:
                        df_pivot = self.pivot_tabla_sumatoria(df)
                else:
                    df_pivot = self.pivot_tabla_sumatoria(df, con_sumatoria=False)

            return df_pivot.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])
        except EmptyResultSet:
            return listado_datos

    def datos_html_table_regiones_ces02(self):
        listado_datos = None
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        pd.set_option('precision', 2)
        pd.options.display.float_format = '{:.2f}'.format

        df = pd.DataFrame(self.listado_datos())
        df.describe()

        for row_index, row in df.iterrows():
            print(row_index, row, sep='\n')
            print(row['segregacion__parametro'])

    @property
    def descargar_excel(self):
        listado_datos = None
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        pd.set_option('precision', 2)
        pd.options.display.float_format = '{:.2f}'.format

        try:
            df = pd.DataFrame(self.listado_datos(para_descargar=True))

            if self.codigo in SEGREGACIONES_PROFUNDIDAD_TRES or self.codigo in SEGREGACIONES_PROFUNDIDAD_TRES_TABS:
                df_pivot = self.datos_table_parametro_opcional(pdt=df)
            elif self.codigo in TABLAS_LINEAL:
                df_pivot = self.pivot_tabla_lineal(df)

                df_pivot.index.names = [LABELS.get(self.codigo, '')]
                df_pivot.columns.names = ['']
            else:
                df_pivot = self.pivot_tabla_sumatoria(df)

            return df_pivot
        except EmptyResultSet:
            return listado_datos

    def datos_plot_totales_bar(self, df):
        df_t = df
        df_t['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)

        df['corte__nombre'] = [str(x) for x in df['corte__nombre']]

        df.rename(columns={'segregacion__parametro': 'Región', 'corte__nombre': 'Período',
                           'segregacion__parametro_opcional': 'Sexo', 'valor': 'Estimación'},
                  inplace=True)

        if self.codigo in ['DU.04', 'DU.05', 'DU.06', 'RH.03', 'RH.04', 'RH.05',  ]:
            df = df.groupby(['Período', 'Región']).sum().round(2)
            df = df.reset_index()
            title = self.nombre
            if self.codigo in ['DU.04']:
                title = "Participantes de nuevo ingreso por recintos"
            elif self.codigo in ['DU.05']:
                title = "Participantes de nuevo ingreso transferidos por recintos"
            fig = px.bar(df, text='Estimación', y='Estimación', x='Período', color='Región', title=title)
            fig.update_layout(barmode='group', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending', },
                              showlegend=True, )

            return plot(fig, output_type='div', include_plotlyjs=False)
        elif self.codigo in ['SU.07', 'SU.08', 'SU.09', 'SU.10', 'SU.11', 'SU.12', ]:
            df = df.groupby(['Período', 'Región']).sum().round(2)
            df = df.reset_index()
            fig = px.bar(df, text='Estimación', y='Estimación', x='Período', color='Región', title=self.nombre)
            fig.update_layout(barmode='group', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending', },
                              showlegend=True, )

            return plot(fig, output_type='div', include_plotlyjs=False)
        else:
            df = df.groupby('Período').sum().round(2)

        # print(pd.pivot_table(df, values="Estimación", index=["Período"], columns=["Región"]))
        fig = px.bar(df, text='value', labels={'value': '', 'Período': ''}, title=self.nombre)
        fig.update_layout(barmode='group', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending', },
                          showlegend=False, )

        return plot(fig, output_type='div', include_plotlyjs=False)

    def datos_plot_promedio_bar(self, df):
        df_t = df
        df_t['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)

        df['corte__nombre'] = [str(x) for x in df['corte__nombre']]
        if self.codigo in PROMEDIOS_BARS:
            df = df.groupby(['corte__nombre', 'segregacion__parametro']).mean().round(3)
            df = df.reset_index()
            fig = px.bar(df, x='corte__nombre', y='valor', color='segregacion__parametro', text='valor',
                         labels={'corte__nombre': '', 'segregacion__parametro': LABELS.get(self.codigo, ''),
                                 'valor': ''}, title=self.nombre)
            fig.update_layout(barmode='group', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending'},
                              showlegend=True, )
            return plot(fig, output_type='div', include_plotlyjs=False)

        df.rename(columns={'segregacion__parametro': 'Región', 'corte__nombre': 'Período',
                           'segregacion__parametro_opcional': 'Sexo', 'valor': 'Estimación'},
                  inplace=True)

        df = df.groupby('Período').mean().round(3)

        fig = px.bar(df, text='value', labels={'value': '', 'Período': ''}, title=self.nombre)
        fig.update_layout(barmode='group', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending'},
                          showlegend=False, )

        return plot(fig, output_type='div', include_plotlyjs=False)

    @property
    def datos_plot_bar(self):
        pd.set_option('precision', 2)
        pd.options.display.float_format = '{:.2f}'.format

        pd.set_option("display.max_rows", None, "display.max_columns", None)
        if self.codigo in NO_BARS:
            return None
        # listado_datos = self.datos.values('segregacion__parametro', 'valor', 'corte__nombre')
        df = pd.DataFrame(list(self.listado_datos()))

        if self.codigo in TOTALES_BARS:
            return self.datos_plot_totales_bar(df)
        elif self.codigo in PROMEDIOS_BARS:
            return self.datos_plot_promedio_bar(df)

        if self.codigo in ['OA.041', ]:
            fig = px.bar(df.sum, x='segregacion__parametro_opcional', y='valor', color='valor', text='valor',
                         labels={'segregacion__parametro_opcional': '', 'valor': ''}, title=self.nombre)

            fig.update_layout(barmode='stack', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending'},
                              autosize=True, width=1000, height=400, showlegend=False, )

            return plot(fig, output_type='div', include_plotlyjs=False)

        elif self.codigo in ['IP.01', 'IP.03', 'EC.01', 'IL.03','IL.04']:
            if self.codigo == 'IP.01':
                labels = {'segregacion__parametro_opcional': 'Recinto', 'corte__nombre': "Corte",
                          'segregacion__parametro': 'Titulación académica', 'valor': 'Investigadores'}
            elif self.codigo == 'IP.03':
                labels = {'segregacion__parametro_opcional': 'Recurso', 'corte__nombre': "Corte",
                          'segregacion__parametro': 'Publicaciones arbitradas', 'valor': 'Publicaciones'}
            elif self.codigo == 'EC.01':
                labels = {'segregacion__parametro_opcional': 'Tipo de oferta', 'corte__nombre': "Corte",
                          'segregacion__parametro': 'Recinto', 'valor': 'Oferta'}
            elif self.codigo == 'IL.03':
                labels = {'segregacion__parametro_opcional': 'Tipo de oferta', 'corte__nombre': "Corte",
                          'segregacion__parametro': 'Recinto', 'valor': 'Cat. laboral'}
            elif self.codigo == 'IL.04':
                labels = {'segregacion__parametro_opcional': 'Tipo de oferta', 'corte__nombre': "Corte",
                          'segregacion__parametro': 'Recinto', 'valor': 'Cat. salarial'}
            fig = px.bar(df, x='corte__nombre', y='valor', text='segregacion__parametro_opcional',
                         color='segregacion__parametro', labels=labels, title=self.nombre)

            fig.update_layout(barmode='group', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending'},
                              autosize=True, width=1000, height=400, showlegend=True, )

            return plot(fig, output_type='div', include_plotlyjs=False)
        fig = px.bar(df, x='corte__nombre', y='valor', color='segregacion__parametro', text='valor',
                     labels={'corte__nombre': '', 'segregacion__parametro': LABELS.get(self.codigo, ''), 'valor': ''},
                     title=self.nombre)
        fig.update_layout(barmode='group', xaxis_tickangle=-45, xaxis={'categoryorder': 'category ascending'},
                          autosize=True, width=1000, height=400)

        return plot(fig, output_type='div', include_plotlyjs=False)

    @property
    def datos_plot_pie(self):
        if self.codigo not in PIE:
            return None
        else:
            df = pd.DataFrame(list(self.listado_datos()))
            # df = px.data.tips()
            fig = px.pie(df, values='valor', names='segregacion__parametro',
                         labels={'segregacion__parametro_opcional': 'Programa', 'segregacion__parametro': 'Recinto',
                                 'valor': 'Participantes retirados'}, title=self.nombre)
            return plot(fig, output_type='div')

    @property
    def datos_plot_line(self):
        import plotly.express as px

        df = pd.DataFrame(list(self.listado_datos()))
        df.rename(columns={'segregacion__parametro': 'Sede', 'corte__nombre': 'Período',
                           'valor': 'Participantes Matriculados'}, inplace=True)

        # df = px.data.gapminder().query("continent=='Oceania'")
        fig = px.line(df, x='Período', y='Participantes Matriculados', color='Sede')
        fig.update_layout(barmode='group', xaxis_tickangle=0, xaxis={'categoryorder': 'category ascending'})

        return plot(fig, output_type='div')

    @property
    def datos_plot_estadisticos(self):
        df = pd.DataFrame(list(self.listado_datos()))
        df.rename(columns={'segregacion__parametro': 'Sede', 'corte__nombre': 'Período',
                           'valor': 'Participantes Matriculados'}, inplace=True)

        fig = px.histogram(df, x='Período', y='Participantes Matriculados', color='Sede', histfunc='avg')

        return plot(fig, output_type='div')

    @property
    def datos_plot_sunburst(self):
        if self.codigo not in SUNBURTS:
            return None
        else:
            df = pd.DataFrame(list(self.listado_datos()))
            df.rename(columns={'segregacion__parametro': LABELS.get(self.codigo, ''), 'corte__nombre': 'Período',
                               'valor': 'Investigadores'}, inplace=True)
            # df = px.data.gapminder().query("year == 2007")
            fig = px.sunburst(df, path=['Período', LABELS.get(self.codigo, ''), 'Investigadores'],
                              values='Investigadores', color=LABELS.get(self.codigo, ''),
                              labels={'segregacion__parametro_opcional': 'Recinto', 'corte__nombre': "Corte",
                                      'segregacion__parametro': 'Titulación académica',
                                      'labels': 'Investigadores'}
                              )
            fig.update_layout(transition_duration=100)
            return plot(fig, output_type='div', include_plotlyjs=False)

    def datossss(self):
        datos = {}
        segregaciones = self.segregacion.annotate(Count('parametro'))
        # if self.codigo == 'CES.01':
        #     print('D1D')
        #     print([it.segregacion_datos() for it in segregaciones][0])
        #     print('D1D')
        #     return
        print(self.segregacion.annotate(Count('parametro')))
        for item in segregaciones:
            datos[item.parametro] = item.segregacion_datos()
        # print('D1D')
        # print(datos)
        # print('D1D')
        return datos

    def __str__(self):
        return f'{self.codigo} {self.nombre}'

    class Meta:
        verbose_name_plural = 'Indicadores'
        ordering = ['pk']


class Algoritmo(models.Model):
    formula = HTMLField()
    unidad_medida = models.CharField(max_length=100, default='Porcentaje')
    metodologia = models.TextField(max_length=650, blank=True, null=True, verbose_name='Metodología de cálculo ')
    descripcion = models.TextField(max_length=255, blank=True, null=True, verbose_name='Descripción')

    indicador = models.ForeignKey(Indicador, on_delete=models.PROTECT, related_name='algoritmos',
                                  related_query_name='algoritmo')

    def __str__(self):
        # return f"{safe(self.formula + 'sdsad </p>')}"
        return "%s" % (str(striptags(self.formula)))

    class Meta:
        ordering = ['formula']


class Termino(models.Model):
    TIPO_CHOICES = [
        ('N', 'Numerador'),
        ('D', 'Denominador'),
        ('C', 'Constante'),
    ]
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default='N', verbose_name='Tipo')
    variable = HTMLField(max_length=25, blank=True, null=True)
    definicion = HTMLField(blank=True, null=True, verbose_name='Definición')

    algoritmo = models.ForeignKey(Algoritmo, on_delete=models.CASCADE, related_name='terminos')

    def indicador(self):
        return self.algoritmo.indicador

    def __str__(self):
        choice = 'Numerador' if self.tipo == 'N' else ('Denominador' if self.tipo == 'D' else 'Constante')
        return f"{choice}: {safe(self.variable)} ({safe(self.algoritmo.indicador.codigo)})"

    class Meta:
        ordering = ['tipo']


class Referencia(models.Model):
    institucion = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='Institución')

    indicador = models.ManyToManyField(Indicador, blank=True, related_name='referencias')

    def __str__(self):
        return f"{self.institucion}"


class FuenteInformacion(models.Model):
    fuente_informacion = models.CharField(max_length=50, verbose_name='Fuente de Información')
    web = models.URLField(null=True, blank=True, verbose_name='Disponible en la web')
    registrado = models.DateField(default=today)

    indicador = models.ForeignKey(Indicador, on_delete=models.PROTECT, blank=True, null=True,
                                  related_name='fuentes_informacion')
    termino = models.ForeignKey(Termino, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.fuente_informacion} [{('Termino: ' + str(self.termino)) if self.termino is not None else ('Indicador' + str(self.indicador.codigo))}]"

    class Meta:
        verbose_name = 'Fuentes de información'
        verbose_name_plural = 'Fuentes de información'


class Segregacion(models.Model):
    parametro = models.CharField(max_length=100, verbose_name='Parámetro',
                                 help_text="Nombre del parámetro para segregar")

    parametro_opcional = models.CharField(max_length=100, blank=True, null=True, verbose_name='Parámetro opcional',
                                          help_text="Nombre del parámetro opcional para segregar")

    indicador = models.ManyToManyField(Indicador, related_name='segregacion', related_query_name='segregacion',
                                       limit_choices_to={'componente__visible': True})

    def __str__(self):
        if self.parametro_opcional:
            return f"{self.parametro}-{self.parametro_opcional}"
        return f"{self.parametro}"

    def segregacion_datos(self):
        datos = self.datos.all()
        tabla = dict()
        tabla['valor'] = [float(item.valor) for item in datos]
        tabla['corte'] = [str(item.corte) for item in datos]
        # tabla['segregacion'] = [item.segregacion for item in datos]

        # print('Datos')
        # print([item.valor for item in datos])
        # print([item.corte for item in datos])
        # print([item.segregacion for item in datos])

        return tabla

    class Meta:
        verbose_name = 'Segregación'
        verbose_name_plural = 'Segregaciones'
        # unique_together = ['parametro', 'parametro_opcional', 'indicador']
