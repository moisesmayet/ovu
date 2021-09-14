from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from ovu.core.forms import DatoForm
from ovu.core.models import Dato, Indicador


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Dato):
            return str(obj)
        return super().default(obj)


class DatoListView(LoginRequiredMixin, generic.View):
    model = Dato
    template_name = 'core/dato/index.html'
    context_object_name = 'dato'
    success_url = reverse_lazy('core:dato_list')
    login_url = 'account_login'

    # def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    #     datos = list(Indicador.objects.filter(visible=True))[0].datos()
    #     pk = kwargs['pk']
    #     print(pk)
    #
    #     context = super().get_context_data(**kwargs)
    #     context['cortes_json'] = json.dumps([str(dat.corte) for dat in datos])
    #     context['valores_json'] = json.dumps([str(dat.valor) for dat in datos])
    #     context['indicadores'] = Indicador.objects.all()
    #     context['indicador'] = Indicador.objects.filter(visible=True).first()
    #     context['datos'] = datos
    #     context['cortes'] = [dat.corte for dat in datos]
    #     context['categorias'] = set([dat.segregacion.parametro or dat.segregacion.parametro_opcional for dat in datos])
    #     context['valores'] = [dat.valor for dat in datos]
    #     return context

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        if pk == 9999:
            pk = Indicador.objects.first().pk
        try:
            indicador = Indicador.objects.get(pk=pk)
        except Indicador.DoesNotExist:
            raise Http404("No existe el indicador")

        datos = indicador.datos()
        datos_formateados = dict()
        headers = []

        for k, v in datos.items():
            datos_formateados[k] = v['valor']
            headers.extend(v['corte'])
        print('--------')
        print(datos_formateados)

        # if indicador.codigo == 'CES.01':
        #     headers.insert(0, 'Categorias')
        # elif indicador.codigo == 'CES.03':
        #     headers.insert(0, 'Nivel/Año')
        headers.insert(0, indicador_switcher(indicador.codigo))

        # request.session.clear()
        request.session['datos'] = datos_formateados
        request.session['headers'] = list(dict.fromkeys(headers))

        context = {}
        # context['cortes_json'] = json.dumps([str(dat.corte) for dat in datos])
        # context['valores_json'] = json.dumps([str(dat.valor) for dat in datos])
        context['indicadores'] = Indicador.objects.all()
        context['indicador'] = indicador
        context['datos'] = datos_formateados
        context['headers'] = list(dict.fromkeys(headers))

        return render(request, self.template_name, context=context)


class DatoCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Dato
    template_name = 'core/dato/form_modal.html'
    form_class = DatoForm
    success_url = reverse_lazy('core:componentes')
    login_url = 'account_login'
    context_object_name = 'form'
    success_message = 'Agregado el dato: %(nombre)s'
    indicador = None

    # def get_initial(self, *args, **kwargs):
    #     initial = super(DatoCreateView, self).get_initial(**kwargs)
    #     print(self.kwargs['componente'])
    #     return initial

    def get_form_kwargs(self, *args, **kwargs):
        form = super().get_form_kwargs()
        form['componente'] = self.kwargs['componente']
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        print(model)
        try:
            pass
            # model.save()
        except ValidationError:
            # messages.warning(request, 'No se puede eliminar la sucursal, posee sucursales asociadas.')
            return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(self.get_success_url())

    # def get_success_url(self) -> str:
    #     return reverse_lazy('core:dato_list', kwargs={'pk': self.model.segregacion.indicador.pk})


dato_create_view = DatoCreateView.as_view()
