from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from .models import UserGroups
from django.contrib.auth.decorators import login_required
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import FormUserGroup
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render_to_response
from django.template import RequestContext
from user_profile.forms import SearchForm
from publications.forms import PublicationForm
import json

class UserGroupCreate(AjaxableResponseMixin, CreateView):
    """
    Vista para la creacion de un grupo
    """
    model = UserGroups
    form_class = FormUserGroup
    http_method_names = [u'post']
    success_url = '/thanks/'

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        owner = get_object_or_404(get_user_model(),
                                    pk=request.POST['owner'])

        # Comprobamos si somos el mismo usuario
        if self.request.user.pk != owner.pk:
            raise IntegrityError()

        print('POST DATA: {}'.format(request.POST))
        print('tipo emitter: {}'.format(type(owner)))
        if form.is_valid():
            print('IS VALID')
            try:
                group = form.save(commit=False)
                group.owner = owner
                group.save()
                # Without this next line the tags won't be saved.
                form.save_m2m()
                print('GROUP CREATED!')
            except IntegrityError as e:
                print("views.py line 30 -> {}".format(e))
            return self.form_valid(form=form)

        print(form.errors)
        return self.form_invalid(form=form)

user_group_create = login_required(UserGroupCreate.as_view(), login_url='/')


class UserGroupList(ListView):
    """
    Vista para listar todos los grupos de la red
    social
    """
    model = UserGroups
    template_name = "groups/list_group.html"

group_list = login_required(UserGroupList.as_view(), login_url='/')


def group_profile(request, groupname):
    """
    Vista del perfil de un grupo
    :param request:
    :param groupname: Nombre del grupo
    """
    user = request.user

    group_profile = get_object_or_404(UserGroups,
                                      slug__iexact=groupname)

    template = "groups/group_profile.html"
    self_initial = {'author': user.pk, 'board_owner': user.pk}
    group_initial = {'owner': user.pk}
    context = {'searchForm': SearchForm(request.POST),
               'publicationSelfForm': PublicationForm(initial=self_initial),
               'groupForm': FormUserGroup(initial=group_initial),
               'group_profile': group_profile}
    return render_to_response(template, context, context_instance=RequestContext(request))


def follow_group(request):
    """
    Vista para seguir a un grupo
    """
    if request.method == 'POST':
        if request.is_ajax():
            user = request.user
            group_id = request.POST.get('id', '')
            print('GROUP ID: {group_id}'.format(**locals()))
            group = get_object_or_404(UserGroups,
                                      pk=group_id)
            try:
                obj, created = group.users.get_or_create(user=user, rol='N')
            except IntegrityError:
                created = False
            if not created:
                response = "in_group"
                return HttpResponse(json.dumps(response), content_type='application/javascript')
            group.save()
            response = "user_add"
            return HttpResponse(json.dumps(response), content_type='application/javascript')
    response = "error"
    return HttpResponse(json.dumps(response), content_type='application/javascript')



