import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from el_pagination.decorators import page_template
from el_pagination.views import AjaxListView
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import FormUserGroup
from .models import UserGroups, LikeGroup, NodeGroup
from neomodel import db
from django.db import transaction
from user_profile.models import NodeProfile


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
        if form.is_valid():
            try:
                group = form.save(commit=False)
                user = self.request.user
                group.owner = user
                group.avatar = request.FILES.get('avatar', None)
                group.back_image = request.FILES.get('back_image', None)
                try:
                    with transaction.atomic():
                        with db.transaction:
                            group.save()
                            g = NodeGroup(group_id=group.id,
                                    title=group.name).save()
                            n = NodeProfile.nodes.get(user_id=user.id)
                            g.members.connect(n)
                except Exception as e:
                    print(e)
                    return self.form_invalid(form=form)
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
    paginate_by = 20


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
    try:
        group_profile = UserGroups.objects.select_related('owner').get(slug=groupname)
    except UserGroups.DoesNotExist:
        raise Http404

    try:
        node_group = NodeGroup.nodes.get(group_id=group_profile.id)
    except NodeGroup.DoesNotExist:
        raise Http404

    group_initial = {'owner': user.pk}
    likes = LikeGroup.objects.filter(to_like=group_profile).count()
    user_like_group = LikeGroup.objects.has_like(group_id=group_profile, user_id=user)
    users_in_group = len(node_group.members.all())

    members = node_group.members.all()
    list_user_id = [x.user_id for x in members]
    user_list = User.objects.filter(id__in=list_user_id)
    context = {'groupForm': FormUserGroup(initial=group_initial),
               'group_profile': group_profile,
               'follow_group': node_group.members.is_connected(NodeProfile.nodes.get(user_id=user.id)) if group_profile.owner_id != user.id else False,
               'likes': likes,
               'user_like_group': user_like_group,
               'users_in_group': users_in_group,
               'group_owner': True if user.id == group_profile.owner_id else False,
               'user_list': user_list}

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
            group = get_object_or_404(UserGroups,
                                      pk=group_id)

            if user.pk != group.owner.pk:
                try:
                    g = NodeGroup.nodes.get(group_id=group_id)
                except NodeGroup.DoesNotExist:
                    g = None
                    #TODO: Return error
                    pass

                try:
                    n = NodeProfile.nodes.get(user_id=user.id)
                except NodeProfile.DoesNotExist:
                    n = None
                    #TODO: Return error
                    pass

                created = g.members.is_connected(n)
                if created:
                    return JsonResponse({
                        'response': "in_group"
                    })

                g.members.connect(n)
                return JsonResponse({
                    'response': "user_add"
                })
            else:
                return JsonResponse({
                    'response': "own_group",
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
                    node_group = NodeGroup.nodes.get(group_id=group_id)
                except NodeGroup.DoesNotExist:
                    #TODO: Return error
                    pass
                try:
                    n = NodeProfile.nodes.get(user_id=user.id)
                except NodeProfile.DoesNotExist:
                    #TODO: Return error
                    pass

                try:
                    node_group.members.disconnect(n)
                    return HttpResponse(json.dumps("user_unfollow"), content_type='application/javascript')
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
        group_id = UserGroups.objects.get(slug__exact=self.kwargs['groupname'])
        node_group = NodeGroup.nodes.get(group_id=group_id.id)
        user_ids = [x.user_id for x in node_group.members.all()]
        return User.objects.filter(id__in=user_ids)


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
                                                              )


likes_group = login_required(LikeListGroup.as_view(), login_url='/')
