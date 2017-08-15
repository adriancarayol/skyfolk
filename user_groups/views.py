import json

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import FormUserGroup
from .models import UserGroups, LikeGroup, NodeGroup
from neomodel import db
from django.db import transaction
from user_profile.models import NodeProfile, TagProfile
from user_profile.utils import make_pagination_html
from django.conf import settings
from PIL import Image
from django.utils import six
from django.core.files.uploadedfile import InMemoryUploadedFile
from publications_groups.forms import PublicationGroupForm
from publications_groups.models import PublicationGroup


class UserGroupCreate(AjaxableResponseMixin, CreateView):
    """
    Vista para la creacion de un grupo
    """
    model = UserGroups
    form_class = FormUserGroup
    http_method_names = [u'post']
    success_url = '/thanks/'

    def __init__(self, **kwargs):
        super(UserGroupCreate, self).__init__(**kwargs)
        self.object = None

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                group = form.save(commit=False)
                user = self.request.user
                group.owner = user
                group.avatar = request.FILES.get('avatar', None)
                image = request.FILES.get('back_image', None)
                if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
                    raise ValueError('BackImage > 5MB!')
                im = Image.open(image).convert('RGBA')
                im.thumbnail((1500, 630), Image.ANTIALIAS)
                tempfile_io = six.BytesIO()
                im.save(tempfile_io, format='JPEG', optimize=True, quality=90)
                tempfile_io.seek(0)
                image_file = InMemoryUploadedFile(tempfile_io, None, 'cover_%s.jpg' % group.name, 'image/jpeg',
                                                  tempfile_io.tell(), None)
                group.back_image = image_file
                tags = form.cleaned_data['tags']
                try:
                    with transaction.atomic():
                        with db.transaction:
                            group.save()
                            g = NodeGroup(group_id=group.id,
                                          title=group.name).save()
                            n = NodeProfile.nodes.get(user_id=user.id)
                            g.members.connect(n)
                            for tag in tags:
                                interest = TagProfile.nodes.get_or_none(title=tag)
                                if not interest:
                                    interest = TagProfile(title=tag).save()
                                if interest:
                                    g.interest.connect(interest)
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

    def get_in_groups(self):
        """
        Obtenemos los grupos
        del usuario que hace la peticion
        """
        results, meta = db.cypher_query(
            "MATCH (n:NodeGroup)-[:MEMBER]-(m:NodeProfile) WHERE m.user_id=%s RETURN n.group_id" % self.request.user.id)
        return [y for x in results for y in x]

    def get_queryset(self):
        groups = self.get_in_groups()
        return UserGroups.objects.filter(id__in=groups)


group_list = login_required(UserGroupList.as_view(), login_url='/')


@login_required(login_url='/')
def group_profile(request, groupname, template='groups/group_profile.html'):
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
               'follow_group': node_group.members.is_connected(
                   NodeProfile.nodes.get(user_id=user.id)) if group_profile.owner_id != user.id else False,
               'likes': likes,
               'user_like_group': user_like_group,
               'users_in_group': users_in_group,
               'publication_group_form': PublicationGroupForm(
                   initial={'author': request.user, 'board_group': group_profile}),
               'publications': PublicationGroup.objects.filter(board_group=group_profile),
               'group_owner': True if user.id == group_profile.owner_id else False,
               'user_list': user_list}

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
                    raise Http404

                try:
                    n = NodeProfile.nodes.get(user_id=user.id)
                except NodeProfile.DoesNotExist:
                    raise Http404

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
                    raise Http404
                try:
                    n = NodeProfile.nodes.get(user_id=user.id)
                except NodeProfile.DoesNotExist:
                    raise Http404

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


class FollowersGroup(ListView):
    """
    Vista con los seguidores (usuarios) de un grupo
    """
    context_object_name = 'user_list'
    template_name = 'groups/followers.html'

    def __init__(self, *args, **kwargs):
        super(FollowersGroup, self).__init__(*args, **kwargs)
        self.pagination = None
        self.group = None

    def get_queryset(self):
        current_page = int(self.request.GET.get('page', '1'))  # page or 1
        limit = 25 * current_page
        offset = limit - 25

        self.group = UserGroups.objects.values('id', 'name').get(slug__exact=self.kwargs['groupname'])
        node_group = NodeGroup.nodes.get(group_id=self.group['id'])
        user_ids = [x.user_id for x in node_group.members.all()[offset:limit]]

        total_users = len(node_group.members.all())
        total_pages = int(total_users / 25)
        if total_users % 25 != 0:
            total_pages += 1
            self.pagination = make_pagination_html(current_page, total_pages)

        return User.objects.filter(id__in=user_ids).select_related('profile')

    def get_context_data(self, **kwargs):
        context = super(FollowersGroup, self).get_context_data(**kwargs)
        context['pagination'] = self.pagination
        context['group'] = self.group
        return context


followers_group = login_required(FollowersGroup.as_view(), login_url='/')


class LikeListGroup(ListView):
    """
    Vista con los usuarios que han dado like a un grupo
    """
    context_object_name = 'like_list'
    template_name = 'groups/user_likes.html'

    def __init__(self, *args, **kwargs):
        super(LikeListGroup, self).__init__(*args, **kwargs)
        self.pagination = None
        self.group = None

    def get_queryset(self):
        current_page = int(self.request.GET.get('page', '1'))  # page or 1
        limit = 25 * current_page
        offset = limit - 25

        self.group = UserGroups.objects.values('id', 'name').get(slug__exact=self.kwargs['groupname'])

        total_users = LikeGroup.objects.filter(to_like_id=self.group['id']).count()
        total_pages = int(total_users / 25)
        if total_users % 25 != 0:
            total_pages += 1
            self.pagination = make_pagination_html(current_page, total_pages)
        return LikeGroup.objects.filter(to_like_id=self.group['id']).values('from_like__username',
                                                                            'from_like__first_name',
                                                                            'from_like__last_name',
                                                                            'from_like__profile__back_image'
                                                                            )

    def get_context_data(self, **kwargs):
        context = super(LikeListGroup, self).get_context_data(**kwargs)
        context['group'] = self.group
        context['pagination'] = self.pagination
        return context


likes_group = login_required(LikeListGroup.as_view(), login_url='/')
