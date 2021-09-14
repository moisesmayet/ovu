from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from ovu.core.views import home_view, about_us_view, componentes_list_view, componente_detail, \
    dato_create_view, indicador_modal_detail_view, indicador_tabla_porcentual, informe_view
from ovu.core.views.indicadores import indicador_tablas, indicador_graficas, indicador_descargar

app_name = "core"
urlpatterns = [
    # path("", TemplateView.as_view(template_name="core/index.html"), name="home"),
    path('', home_view, name='home'),
    path('about_us', about_us_view, name='about_us'),
    path('faq', TemplateView.as_view(template_name="core/faq.html"), name='faq'),
    path('componentes', (cache_page(60 * 0))(componentes_list_view), name='componentes'),
    path('componente/<int:pk>', (componente_detail), name='componente_detalles'),

    # Datos
    path('dato/<int:componente>', dato_create_view, name='dato_add'),

    # Indicadores
    path('indicador/<int:pk>', indicador_modal_detail_view, name='indicador_modal_detail'),
    path('indicador/tp/<int:pk>', (indicador_tablas), name='indicador_tablas'),
    path('indicador/tg/<int:pk>', (cache_page(60 * 0))(indicador_graficas), name='indicador_graficas'),
    path('indicador/tp/<int:pk>', (indicador_tabla_porcentual), name='indicador_tabla_porcentual'),
    path('indicador/descargar/<int:indicador>', indicador_descargar, name='indicador_descargar'),

    # Informes
    path('informes', informe_view, name='informes'),

]
