from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_http_methods

from ovu.core.configuraciones import TABS
from ovu.core.forms import IndicadorForm
from ovu.core.models import Indicador
from ovu.core.models.indicador import SEGREGACIONES_PROFUNDIDAD_TRES_TABS


class IndicadorListView(LoginRequiredMixin, generic.ListView):
    model = Indicador
    template_name = 'core/indicador/index.html'
    context_object_name = 'object'
    login_url = 'account_login'
    paginate_by = 15


class IndicadorAddView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Indicador
    template_name = 'core/indicador/form_modal.html'
    form_class = IndicadorForm
    success_url = reverse_lazy('core:indicador_list')
    login_url = 'account_login'
    context_object_name = 'form'
    success_message = 'Agregado el Indicador: %(nombre)s'


class IndicadorUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Indicador
    template_name = 'core/indicador/form_modal.html'
    form_class = IndicadorForm
    success_url = reverse_lazy('core:indicador_list')
    login_url = 'account_login'
    context_object_name = 'form'
    success_message = 'Actualizado el Indicador: %(nombre)s'


class IndicadorDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Indicador
    template_name = 'core/indicador/delete_modal.html'
    success_url = reverse_lazy('core:indicador_list')
    login_url = 'account_login'
    success_message = 'Eliminado el Indicador: %(nombre)s'

    def delete(self, request, *args: str, **kwargs):
        self.success_message = f'Eliminado el Indicador {self.get_object().nombre}'
        messages.warning(self.request, self.success_message)
        return super(IndicadorDeleteView, self).delete(request, *args, **kwargs)


class IndicadorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Indicador
    template_name = 'core/indicador/detail.html'
    success_url = reverse_lazy('core:indicador_list')
    login_url = 'account_login'


class IndicadorModalDetailView(generic.DetailView):
    model = Indicador
    context_object_name = 'indicador'
    template_name = 'core/indicador/detail_modal.html'
    success_url = reverse_lazy('core:componentes')
    login_url = 'account_login'


indicador_modal_detail_view = IndicadorModalDetailView.as_view()


@require_http_methods(["GET"])
def indicador_tabla_porcentual(request, pk):
    template_name = 'core/indicador/tabla_porcentual.html'
    context = {}
    indicador = Indicador.objects.get(id=pk)

    context['indicador'] = indicador
    return render(request, template_name, context)


@require_http_methods(["GET"])
def indicador_tablas(request, pk):
    template_name = 'core/indicador/modal_table.html'
    context = {}
    indicador = Indicador.objects.get(id=pk)

    context['indicador'] = indicador
    context['indicadores_tabs'] = TABS
    if indicador.codigo in TABS:
        context['tablas'], context['anos_tabs'] = indicador.datos_html_table
        # print(context['tablas'])
        # print(context['anos_tabs'])
        # print(context['anos_tabs']+context['tablas'])
    return render(request, template_name, context)


@require_http_methods(["GET"])
def indicador_graficas(request, pk):
    template_name = 'core/indicador/modal_graficas.html'
    context = {}
    indicador = Indicador.objects.get(id=pk)

    context['nombre'] = indicador.nombre
    context['codigo'] = indicador.codigo
    context['bar'] = indicador.datos_plot_bar
    # context['pie'] = indicador.datos_plot_pie
    # context['line'] = indicador.datos_plot_line
    context['sunburst'] = indicador.datos_plot_sunburst
    return render(request, template_name, context)


@require_http_methods(["GET"])
def indicador_descargar(request, indicador):
    indicador = Indicador.objects.get(id=indicador)

    response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-16')
    response[
        'Content-Disposition'] = f'attachment; filename={indicador.codigo}.xlsx'
    indicador.descargar_excel.to_excel(response, index=True)
    return response
