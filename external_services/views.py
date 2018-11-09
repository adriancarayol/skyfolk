from django.views.generic.list import ListView
from external_services.models import Services
from django.contrib.auth.decorators import login_required


class ListServiceView(ListView):
    model = Services
    paginate_by = 100
    template_name = 'external_services/services.html'


list_service_view = login_required(ListServiceView.as_view())
