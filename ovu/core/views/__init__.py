from .core import home_view, about_us_view
from .ovu import OvuCreateView
from .componente import componentes_list_view, componente_detail, ComponenteUpdateView, ComponenteDeleteView, \
    ComponenteAddView
from .indicadores import IndicadorListView, IndicadorUpdateView, IndicadorDeleteView, IndicadorAddView, \
    IndicadorDetailView, indicador_modal_detail_view, indicador_tabla_porcentual
from .dato import DatoListView, dato_create_view
from .graphics import plot, dashboard_plot
from .dashboard import DashboardView
from .informe import informe_view
