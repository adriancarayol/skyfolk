import json
import logging
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views import View
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import FormUserGroup
from .models import UserGroups, LikeGroup, NodeGroup, RequestGroup
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
from guardian.shortcuts import assign_perm, remove_perm
from django.core.exceptions import ObjectDoesNotExist
from notifications.signals import notify
from notifications.models import Notification
from user_profile.tasks import send_email


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
                if image:
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
                            g = NodeGroup(group_id=group.group_ptr_id,
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
        return UserGroups.objects.filter(group_ptr_id__in=groups)


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

    try:
        friend_request = RequestGroup.objects.get_follow_request(
                from_profile=user.id, to_group=group_profile)
    except ObjectDoesNotExist:
        friend_request = None

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
               'friend_request': friend_request,
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
                                      group_ptr_id=group_id)

            if user.pk != group.owner.pk:
                try:
                    g = NodeGroup.nodes.get(group_id=group_id)
                    n = NodeProfile.nodes.get(user_id=user.id)
                except ObjectDoesNotExist:
                    raise Http404

                created = g.members.is_connected(n)

                if created:
                    return JsonResponse({
                        'response': "in_group"
                    })

                if group.is_public:
                    try:
                        with transaction.atomic(using="default"):
                            with db.transaction:
                                g.members.connect(n)
                                assign_perm('can_publish', user, group)
                                return JsonResponse({
                                    'response': "user_add"
                                })
                    except Exception:
                        return JsonResponse({
                            'response': "error"
                    })
                else:
                    # Recuperamos peticion al grupo
                    try:
                        group_request = RequestGroup.objects.get_follow_request(user, group)
                    except ObjectDoesNotExist:
                        group_request = None

                    # Si no existe, creamos una nueva
                    if not group_request:
                        Notification.objects.filter(actor_object_id=user.id, recipient=group.owner,
                                level='grouprequest').delete()
                        try:
                            with transaction.atomic(using="default"):
                                request_group = RequestGroup.objects.add_follow_request(user.id,
                                        group.id)

                                notify.send(user,
                                        actor=user.username,
                                        recipient=group.owner, verb=u'%s solicita unirse al grupo %s'
                                        % (user.username, group.name), level='grouprequest', action_object=request_group)

                        except IntegrityError:
                            return JsonResponse({
                                'response': "no_added_group"
                            })
                        send_email.delay('Skyfolk - %s quiere seguirte.' % user.username, [group.owner.email],
                            {'to_user': group.owner.username, 'from_user': user.username,
                                'to_group': group.name},
                            'emails/member_request.html')

                    return JsonResponse({
                        'response': 'in_progress'
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
            group = get_object_or_404(UserGroups, group_ptr_id=group_id)
            if user.pk != group.owner.pk:
                try:
                    node_group = NodeGroup.nodes.get(group_id=group_id)
                    n = NodeProfile.nodes.get(user_id=user.id)
                except ObjectDoesNotExist:
                    raise Http404

                try:
                    with transaction.atomic(using="default"):
                        with db.transaction:
                            node_group.members.disconnect(n)
                            remove_perm('can_publish', user, group)
                    return HttpResponse(json.dumps("user_unfollow"), content_type='application/javascript')
                except (ObjectDoesNotExist, Exception) as e:
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
                                      group_ptr_id=group_id)

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

        self.group = UserGroups.objects.get(slug__exact=self.kwargs['groupname'])
        node_group = NodeGroup.nodes.get(group_id=self.group.group_ptr_id)
        user_ids = [x.user_id for x in node_group.members.all()[offset:limit]]

        total_users = len(node_group.members.all())
        total_pages = int(total_users / 25)
        if total_users % 25 != 0:
            total_pages += 1
            self.pagination = make_pagination_html(current_page, total_pages)

        return User.objects.filter(id__in=user_ids).select_related('profile')

    def get_context_data(self, **kwargs):
        context = super(FollowersGroup, self).get_context_data(**kwargs)
        user = self.request.user
        context['pagination'] = self.pagination
        context['group'] = self.group
        context['enable_kick_btn'] = user.has_perm('kick_member', self.group)
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

class RespondGroupRequest(View):
    http_method = ['post', ]

    def post(self, request, **kwargs):
        user = request.user
        request_id = int(request.POST.get('slug', None))
        request_status = request.POST.get('status', None)
        response = 'error'
        try:
            request_group = RequestGroup.objects.select_related('emitter').get(id=request_id)
            group = UserGroups.objects.get(group_ptr_id=request_group.receiver_id)
        except ObjectDoesNotExist:
            return JsonResponse({'response': response})

        if request_status == 'accept':
            if user.id == group.owner_id:
                try:
                    g = NodeGroup.nodes.get(group_id=group.group_ptr_id)
                    n = NodeProfile.nodes.get(user_id=request_group.emitter_id)
                except ObjectDoesNotExist:
                    return JsonResponse({'response': response})
                try:
                    with transaction.atomic(using="default"):
                        with db.transaction:
                            request_group.delete()
                            g.members.connect(n)
                            notify.send(user, actor=user.username,
                                recipient=request_group.emitter,
                                verb=u'¡ahora eres miembro de <a href="/group/%s">%s</a>!.' % (group.name, group.name),
                                level='new_member_group')
                except Exception as e:
                    return JsonResponse({'response': 'error'})

                response = "added_friend"
                send_email.delay('Skyfolk - %s ha aceptado tu solicitud.' % user.username, [request_group.emitter.email],
                             {'to_user': request_group.emitter.username, 'from_group': group.name},
                             'emails/new_member_added.html')
        elif request_status == 'rejected':
            if user.id == group.owner_id:
                try:
                    with transaction.atomic(using="default"):
                        request_group.delete()
                    response = 'removed'
                except ObjectDoesNotExist:
                    pass

        return JsonResponse({'response': response})


respond_group_request = login_required(RespondGroupRequest.as_view(), login_url='/')


class RemoveRequestFollow(View):

    http_method = ['post', ]

    def post(self, request, **kwargs):
        user = request.user
        response = False
        slug = int(request.POST.get('slug', None))
        status = request.POST.get('status', None)

        if status == 'cancel':
            try:
                request_group = RequestGroup.objects.remove_received_follow_request(from_profile=user.id,
                        to_group=slug)
            except ObjectDoesNotExist:
                response = False
            response = True
        return JsonResponse({'response': response})

remove_group_request = login_required(RemoveRequestFollow.as_view(), login_url='/')

class KickMemberGroup(View):
    http_method = ['post', ]

    def post(self, request, **kwargs):
        user = request.user
        response = 'error'
        user_id = int(request.POST.get('id', None))
        group_id = int(request.POST.get('group_id', None))

        try:
            group = UserGroups.objects.get(group_ptr_id=group_id)
        except ObjectDoesNotExist:
            return JsonResponse({'response': 'error'})

        if user_id == user.id:
            return JsonResponse({'response': 'is_owner'})

        if user.has_perm('kick_member', group):
            try:
                n = NodeProfile.nodes.get(user_id=user_id)
                g = NodeGroup.nodes.get(group_id=group.group_ptr_id)
            except ObjectDoesNotExist:
                return JsonResponse({'response': response})

            g.members.disconnect(n)
            response = 'kicked'

        return JsonResponse({'response': response})

kick_member = login_required(KickMemberGroup.as_view(), login_url='/')
