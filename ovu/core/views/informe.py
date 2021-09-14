from django.views import generic

from ovu.core.models import Informe


class IndicadorListView(generic.ListView):
    model = Informe
    template_name = 'core/informe/index.html'
    queryset = Informe.objects.filter(visible=True)
    context_object_name = 'informes'
    login_url = 'account_login'


informe_view = IndicadorListView.as_view()
