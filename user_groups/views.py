import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from el_pagination.decorators import page_template
from el_pagination.views import AjaxListView

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
@page_template('groups/user_entries.html')
def group_profile(request, groupname, template='groups/group_profile.html',
                  extra_context=None):
    """
    Vista del perfil de un grupo
    :param request:
    :param groupname: Nombre del grupo
    """
    user = request.user
    group_profile = get_object_or_404(UserGroups,
                                      slug__exact=groupname)
    follow_group = UserGroups.objects.is_follow(group_id=group_profile.id,
                                                user_id=user)
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
               'users_in_group': users_in_group,
               'notifications': user.notifications.unread(),
               'user_list': group_profile.users.all().values('user__username', 'user__first_name',
                                                             'user__last_name')}

    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


@login_required(login_url='/')
def follow_group(request):
    """
    Vista para seguir a un grupo
    """
    if request.method == 'POST':
        if request.is_ajax():
            user = request.user
            group_id = request.POST.get('id', None)
            print('GROUP ID: {group_id}'.format(**locals()))
            group = get_object_or_404(UserGroups,
                                      pk=group_id)
            try:
                if user.pk != group.owner.pk:
                    obj, created = group.users.get_or_create(
                        user=user, rol='N')
                else:
                    return JsonResponse({
                        'response': "own_group",
                    })
            except IntegrityError:
                created = False
            if not created:
                return JsonResponse({
                    'response': "in_group"
                })
            group.save()
            return JsonResponse({
                'response': "user_add"
            })
    return JsonResponse({
        'response': "error"
    })


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
    if request.method == 'POST':
        if request.is_ajax():
            user = request.user
            group_id = request.POST.get('id', None)
            group = get_object_or_404(UserGroups,
                                      pk=group_id)

            print('user_pk: {} owner_pk: {}'.format(user.pk, group.owner.pk))
            if user.pk == group.owner.pk:
                return JsonResponse(
                    {'response': 'own_group'})

            like, created = LikeGroup.objects.get_or_create(
                from_like=user, to_like=group)
            print('Like: {}'.format(like))
            if not created:
                like.delete()
                return JsonResponse({'response': 'no_like'})
            else:
                return JsonResponse({'response': 'like'})
    return JsonResponse(
        {'response': 'error'})


class FollowersGroup(AjaxListView):
    """
    Vista con los seguidores (usuarios) de un grupo
    """
    context_object_name = 'user_list'
    template_name = 'groups/followers.html'
    page_template = 'groups/followers_page.html'

    def get_queryset(self):
        return UserGroups.objects.get(slug__exact=self.kwargs['groupname']).users.all()


followers_group = login_required(FollowersGroup.as_view(), login_url='/')


class LikeListGroup(AjaxListView):
    """
    Vista con los usuarios que han dado like a un grupo
    """
    context_object_name = 'like_list'
    template_name = 'groups/user_likes.html'
    page_template = 'groups/user_list_page.html'

    def get_queryset(self):
        group = UserGroups.objects.get(slug__exact=self.kwargs['groupname'])
        return LikeGroup.objects.filter(to_like=group).values('from_like__username',
                                                              'from_like__first_name', 'from_like__last_name',
                                                              'from_like__profile__backImage')


likes_group = login_required(LikeListGroup.as_view(), login_url='/')
