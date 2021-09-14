from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from ovu.core.models import Indicador, Componente


def indicadores_visibles() -> int: return Indicador.objects.filter(visible=True).count()


def componentes_visibles() -> int: return Componente.objects.filter().count()


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context['componentes'] = componentes_visibles()
        context['indicadores'] = indicadores_visibles()

        return render(request, self.template_name, context=context)
