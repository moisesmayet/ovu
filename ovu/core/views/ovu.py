from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.views import generic

from ovu.core.forms import OvuForm
from ovu.core.models import Ovu


class OvuCreateView(LoginRequiredMixin, generic.CreateView):
    model = Ovu
    template_name = 'core/ovu.html'
    form_class = OvuForm
    context_object_name = 'ovu'
    login_url = 'account_login'
