from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from ovu.core.models import Componente, Indicador


class HomeView(generic.View):
    template_name = 'core/index.html'
    success_url = reverse_lazy('core:dato_list')

    def get(self, request, *args, **kwargs):
        context = {}
        context['total_componentes'] = Componente.total_componentes()
        context['total_indicadores'] = Indicador.total_indicadores_visibles()
        context['componentes'] = Componente.objects.filter(visible=True)
        return render(request, self.template_name, context=context)


home_view = HomeView.as_view()


class AboutUsView(generic.View):
    template_name = 'core/about-us.html'
    success_url = reverse_lazy('core:dato_list')

    def get(self, request, *args, **kwargs):
        context = {}
        context['total_componentes'] = Componente.total_componentes()
        context['total_indicadores'] = Indicador.total_indicadores_visibles()
        return render(request, self.template_name, context=context)


about_us_view = AboutUsView.as_view()
