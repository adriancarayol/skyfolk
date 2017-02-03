import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from publications.forms import PublicationForm
from user_profile.forms import SearchForm
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import FormUserGroup
from .models import UserGroups, LikeGroup


class UserGroupCreate(AjaxableResponseMixin, CreateView):
    """
    Vista para la creacion de un grupo
    """
    model = UserGroups
    form_class = FormUserGroup
    http_method_names = [u'post']
    success_url = '/thanks/'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def post(self, request, *args, **kwargs):
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


@login_required(login_url='/')
def group_profile(request, groupname):
    """
    Vista del perfil de un grupo
    :param request:
    :param groupname: Nombre del grupo
    """
    user = request.user
    group_profile = get_object_or_404(UserGroups,
                                      slug__iexact=groupname)
    follow_group = UserGroups.objects.is_follow(group_id=group_profile.id,
                                                user_id=user)
    print('Usuario: {} sigue a: {}, {}'.format(user.username, group_profile.name, follow_group))
    template = "groups/group_profile.html"
    self_initial = {'author': user.pk, 'board_owner': user.pk}
    group_initial = {'owner': user.pk}
    likes = LikeGroup.objects.filter(to_like=group_profile).count()
    user_like_group = LikeGroup.objects.has_like(group_id=group_profile, user_id=user)
    users_in_group = group_profile.users.count()
    context = {'searchForm': SearchForm(request.POST),
               'publicationSelfForm': PublicationForm(initial=self_initial),
               'groupForm': FormUserGroup(initial=group_initial),
               'group_profile': group_profile,
               'follow_group': follow_group,
               'likes': likes,
               'user_like_group': user_like_group,
               'users_in_group': users_in_group}
    return render(request, template, context)


@login_required(login_url='/')
def follow_group(request):
    """
    Vista para seguir a un grupo
    """
    response = "error"
    if request.method == 'POST':
        if request.is_ajax():
            user = request.user
            group_id = request.POST.get('id', None)
            print('GROUP ID: {group_id}'.format(**locals()))
            group = get_object_or_404(UserGroups,
                                      pk=group_id)
            try:
                if user.pk != group.owner.pk:
                    obj, created = group.users.get_or_create(user=user, rol='N')
                else:
                    return HttpResponse(json.dumps(response), content_type='application/javascript')
            except IntegrityError:
                created = False
            if not created:
                response = "in_group"
                return HttpResponse(json.dumps(response), content_type='application/javascript')
            group.save()
            response = "user_add"
            return HttpResponse(json.dumps(response), content_type='application/javascript')
    return HttpResponse(json.dumps(response), content_type='application/javascript')


@login_required(login_url='/')
def unfollow_group(request):
    """
    Vista para dejar de seguir a un grupo
    """
    if request.method == 'POST':
        if request.is_ajax():
            user = request.user
            group_id = request.POST.get('id', None)
            group = get_object_or_404(UserGroups, pk=group_id)
            if user.pk != group.owner.pk:
                try:
                    group.users.filter(user=user).delete()
                    try:
                        group.save()
                        return HttpResponse(json.dumps("user_unfollow"), content_type='application/javascript')
                    except IntegrityError:
                        return HttpResponse(json.dumps("error"), content_type='application/javascript')
                except UserGroups.DoesNotExist:
                    return HttpResponse(json.dumps("error"), content_type='application/javascript')
            else:
                return HttpResponse(json.dumps("error"), content_type='application/javascript')
    return HttpResponse(json.dumps("error"), content_type='application/javascript')


@login_required(login_url='/')
def like_group(request):
    """
    Funcion para dar like al perfil
    """
    response = "error"
    if request.method == 'POST':
        if request.is_ajax():
            user = request.user
            group_id = request.POST.get('id', None)
            group = get_object_or_404(UserGroups,
                                      pk=group_id)

            if user.pk == group.owner.pk:
                return HttpResponse(json.dumps(response), content_type='application/javascript')

            like, created = LikeGroup.objects.get_or_create(from_like=user, to_like=group)

            if not created:
                like.delete()
                response = "no_like"
            else:
                response = "like"
            print('Like: {}'.format(like))
            return HttpResponse(json.dumps(response), content_type='application/javascript')
    return HttpResponse(json.dumps(response), content_type='application/javascript')
