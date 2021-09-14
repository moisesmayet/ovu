# Create your views here.
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.cache import cache_page

from ovu.core.forms import ComponenteForm
from ovu.core.models import Componente



class ComponentesListView(generic.ListView):
    model = Componente
    queryset = Componente.objects.filter(visible=True)
    template_name = 'core/componente/index.html'
    context_object_name = 'componentes'
    login_url = 'account_login'
    paginate_by = 15


componentes_list_view = ComponentesListView.as_view()


class ComponenteAddView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Componente
    template_name = 'core/componente/form_modal.html'
    form_class = ComponenteForm
    success_url = reverse_lazy('core:componente_list')
    login_url = 'account_login'
    context_object_name = 'form'
    success_message = 'Agregado el componente: %(nombre)s'


class ComponenteUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Componente
    template_name = 'core/componente/form_modal.html'
    form_class = ComponenteForm
    success_url = reverse_lazy('core:componente_list')
    login_url = 'account_login'
    context_object_name = 'form'
    success_message = 'Actualizado el componente: %(nombre)s'


class ComponenteDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Componente
    template_name = 'core/componente/delete_modal.html'
    success_url = reverse_lazy('core:componente_list')
    login_url = 'account_login'
    success_message = 'Eliminado el componente: %(nombre)s'

    def delete(self, request, *args: str, **kwargs):
        if self.get_object().indicadores.count() > 0:
            self.success_message = f'No se puede eliminar el componente {self.get_object().nombre}, tiene {self.get_object().indicadores.count()} indicadores'
            messages.warning(self.request, self.success_message)
            return redirect('core:componente_list')
        else:
            self.success_message = f'Eliminado el componente {self.get_object().nombre}'
        messages.warning(self.request, self.success_message)
        return super(ComponenteDeleteView, self).delete(request, *args, **kwargs)



class ComponenteDetailView(generic.DetailView):
    model = Componente
    context_object_name = 'componente'
    template_name = 'core/componente/detail.html'
    login_url = 'account_login'


componente_detail = ComponenteDetailView.as_view()
