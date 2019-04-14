from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from external_services.models import Services, UserService


class ListServiceView(ListView):
    paginate_by = 100
    model = Services
    template_name = "external_services/services.html"
    context_object_name = "services_list"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["active_services"] = UserService.objects.filter(
            user=user
        ).select_related("service")
        return context

    def get_queryset(self):
        user = self.request.user
        user_services = UserService.objects.filter(user=user).values_list(
            "service_id", flat=True
        )
        return Services.objects.exclude(id__in=user_services)


def delete_user_service_view(request, pk):
    if request.method == "POST" and request.is_ajax():
        user = request.user

        try:
            UserService.objects.filter(user=user, pk=pk).delete()
            return JsonResponse({"delete": "yes"})
        except ObjectDoesNotExist:
            raise Http404

    return JsonResponse(status=400, data={"delete": "no"})


list_service_view = login_required(ListServiceView.as_view())
delete_user_service_view = login_required(delete_user_service_view)
