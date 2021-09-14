from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory
from tinymce.widgets import TinyMCE

from ovu.core.models import Ovu, Objetivos, Componente, Indicador, Dato


class OvuForm(forms.ModelForm):
    class Meta:
        model = Ovu
        fields = '__all__'


OvuObjetivosFormSet = inlineformset_factory(Ovu, Objetivos, form=OvuForm, fields=['objetivo'], extra=1, can_delete=True)
BookFormSet = inlineformset_factory(Ovu, Objetivos, fields='__all__')


class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = '__all__'


class IndicadorForm(forms.ModelForm):
    observaciones = forms.CharField(widget=TinyMCE(attrs={'cols': 10, 'rows': 10}))

    class Meta:
        model = Indicador
        fields = '__all__'


class DatoForm(forms.ModelForm):
    class Meta:
        model = Dato
        fields = '__all__'

    def __init__(self, componente, *args, **kwargs):
        super(DatoForm, self).__init__(*args, **kwargs)
        self.fields['indicador'].queryset = Indicador.objects.filter(componente__pk=componente)

    def clean(self):
        cleaned_data = self.cleaned_data

        try:
            Dato.objects.get(segregacion=cleaned_data['segregacion'], corte=cleaned_data['corte'])
        except Dato.DoesNotExist:
            pass
        else:
            raise ValidationError('Solution with this Name already exists for this problem')
        return cleaned_data
