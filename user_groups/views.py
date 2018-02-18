import json
import logging

from PIL import Image
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import IntegrityError, transaction
from django.db import transaction
from django.db.models import Q, Count, Case, When, Value, IntegerField, OuterRef, Subquery

from django.http import HttpResponseForbidden, Http404, JsonResponse
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import six
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from guardian.shortcuts import remove_perm
from neomodel import db
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.signals import notify
from publications.models import Publication
from publications_groups.forms import PublicationGroupForm, GroupPublicationEdit, PublicationThemeForm
from publications.forms import SharedPublicationForm
from publications_groups.models import PublicationGroup
from publications_groups.themes.models import PublicationTheme
from user_groups.forms import GroupThemeForm, EditGroupThemeForm
from user_groups.models import GroupTheme, LikeGroupTheme, HateGroupTheme
from user_profile.models import RelationShipProfile, BLOCK, Profile
from user_profile.node_models import NodeProfile, TagProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import FormUserGroup, GroupThemeForm
from .models import UserGroups, LikeGroup, RequestGroup
from user_groups.node_models import NodeGroup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators import user_can_view_group, user_can_view_group_info


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

                    im = Image.open(image)
                    fill_color = (255, 255, 255, 0)

                    if im.mode in ('RGBA', 'LA'):
                        background = Image.new(im.mode[:-1], im.size, fill_color)
                        background.paste(im, im.split()[-1])
                        im = background

                    im.thumbnail((1500, 630), Image.ANTIALIAS)
                    tempfile_io = six.BytesIO()
                    im.save(tempfile_io, format='JPEG', optimize=True, quality=90)
                    tempfile_io.seek(0)
                    image_file = InMemoryUploadedFile(tempfile_io, None, 'cover_%s.jpg' % group.name, 'image/jpeg',
                                                      tempfile_io.tell(), None)
                    group.back_image = image_file
                tags = form.cleaned_data.get('tags', None)
                try:
                    with transaction.atomic():
                        with db.transaction:
                            group.save()
                            g = NodeGroup(group_id=group.id,
                                          title=group.name).save()
                            n = NodeProfile.nodes.get(user_id=user.id)
                            group.users.add(user)
                            g.members.connect(n)
                            if tags:
                                for tag in tags:
                                    group.tags.add(tag)
                                    interest = TagProfile.nodes.get_or_none(title=tag)
                                    if not interest:
                                        interest = TagProfile(title=tag).save()
                                    if interest:
                                        g.interest.connect(interest)
                except Exception as e:
                    print(e)
                    return self.form_invalid(form=form)
            except IntegrityError as e:
                return self.form_invalid(form=form)

            return self.form_valid(form=form,
                                   msg='¡Tu grupo ha sido creado, haz click <a href="{0}">aquí</a> para visitarlo.'.format(
                                       reverse_lazy('user_groups:group-profile', kwargs={'groupname': group.slug})))

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

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserGroupList, self).dispatch(request, *args, **kwargs)

    def get_in_groups(self):
        """
        Obtenemos los grupos
        del usuario que hace la peticion
        """
        results, meta = db.cypher_query(
            "MATCH (n:NodeGroup)-[:MEMBER]-(m:NodeProfile) WHERE m.user_id=%s RETURN n.group_id" % self.request.user.id)
        return [y for x in results for y in x]

    def get_queryset(self):
        return UserGroups.objects.filter(id__in=self.request.user.user_groups.all())


@user_can_view_group
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

    try:
        n = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        raise Http404

    is_member = False
    if group_profile.owner_id != user.id:
        if node_group.members.is_connected(n):
            is_member = True

    is_ajax = False

    if request.is_ajax():
        page = request.GET.get('page', 1)
        qs = request.GET.get('qs', None)
        is_ajax = True
    else:
        page = 1
        qs = None

    if is_ajax and qs == 'themes':
        template = 'groups/group_themes.html'

        theme_publications = PublicationTheme.objects.filter(board_theme=OuterRef('pk'),
                                                             deleted=False).order_by().values(
            'board_theme')

        total_theme_publications = theme_publications.annotate(c=Count('*')).values('c')

        themes = GroupTheme.objects.filter(board_group_id=group_profile.id).annotate(
            likes=Count('like_theme'),
            hates=Count('hate_theme')).annotate(
            have_like=Count(Case(
                When(like_theme__by_user_id=user.id, then=Value(1)),
                output_field=IntegerField()
            ))).annotate(have_hate=Count(Case(
            When(hate_theme__by_user_id=user.id, then=Value(1)),
            output_field=IntegerField()
        ))).annotate(total_pubs=Subquery(total_theme_publications, output_field=IntegerField())).select_related('owner')

        paginator = Paginator(themes, 20)

        try:
            themes = paginator.page(page)
        except PageNotAnInteger:
            themes = paginator.page(1)
        except EmptyPage:
            themes = paginator.page(paginator.num_pages)

        context = {
            'themes': themes
        }
        return render(request, template, context)

    shared_publications = Publication.objects.filter(shared_group_publication__id=OuterRef('pk'),
                                                     deleted=False).order_by().values(
        'shared_group_publication__id')

    total_shared_publications = shared_publications.annotate(c=Count('*')).values('c')

    shared_for_me = shared_publications.annotate(have_shared=Count(Case(
        When(author_id=user.id, then=Value(1))
    ))).values('have_shared')

    users_not_blocked_me = RelationShipProfile.objects.filter(
        to_profile=user.profile, type=BLOCK).values('from_profile_id')

    publications = PublicationGroup.objects.annotate(likes=Count('user_give_me_like'),
                                                     hates=Count('user_give_me_hate'), have_like=Count(Case(
            When(user_give_me_like__id=user.id, then=Value(1)),
            output_field=IntegerField()
        )), have_hate=Count(Case(
            When(user_give_me_hate__id=user.id, then=Value(1)),
            output_field=IntegerField()
        ))).annotate(total_shared=Subquery(total_shared_publications, output_field=IntegerField())).annotate(
        have_shared=Subquery(shared_for_me, output_field=IntegerField())).filter(Q(board_group=group_profile) &
                                                                                 Q(deleted=False) & Q(
        level__lte=0) & ~Q(
        author__profile__in=users_not_blocked_me)) \
        .prefetch_related('group_extra_content', 'images',
                          'videos', 'user_give_me_like', 'user_give_me_hate', 'tags') \
        .select_related('author',
                        'board_group',
                        'parent')

    paginator = Paginator(publications, 20)

    try:
        publications = paginator.page(page)
    except PageNotAnInteger:
        publications = paginator.page(1)
    except EmptyPage:
        publications = paginator.page(paginator.num_pages)

    if is_ajax and qs == 'publications':
        template = 'groups/comentarios_entries.html'
        context = {
            'publications': publications,
            'enable_control_pubs_btn': user.has_perm('delete_publication', group_profile),
            'group_profile': group_profile
        }
        return render(request, template, context)

    likes = LikeGroup.objects.filter(to_like=group_profile).count()
    user_like_group = LikeGroup.objects.has_like(group_id=group_profile, user_id=user)
    users_in_group = len(node_group.members.all())

    group_initial = {'owner': user.pk}

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
               'follow_group': is_member,
               'likes': likes,
               'user_like_group': user_like_group,
               'users_in_group': users_in_group,
               'publication_group_form': PublicationGroupForm(
                   initial={'author': request.user, 'board_group': group_profile}),
               'publications': publications,
               'group_owner': True if user.id == group_profile.owner_id else False,
               'friend_request': friend_request,
               'enable_control_pubs_btn': user.has_perm('delete_publication', group_profile),
               'interests': node_group.interest.match(),
               'share_publication': SharedPublicationForm(),
               'publication_edit': GroupPublicationEdit(),
               'theme_form': GroupThemeForm(initial={'owner': request.user, 'board_group': group_profile}),
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
                                      id=group_id)

            if user.pk != group.owner.pk:
                try:
                    g = NodeGroup.nodes.get(group_id=group_id)
                    n = NodeProfile.nodes.get(user_id=user.id)
                except (NodeGroup.DoesNotExist, NodeProfile.DoesNotExist) as e:
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
                                group.users.add(user)
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
                                            recipient=group.owner,
                                            description="@{0} solicita unirse al grupo {1}.".format(user.username,
                                                                                                    group.name),
                                            verb=u'<a href="/profile/{0}/">@{0}</a> solicita unirse al grupo {1}'.format(
                                                user.username, group.name),
                                            level='grouprequest', action_object=request_group)

                        except IntegrityError:
                            return JsonResponse({
                                'response': "no_added_group"
                            })

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
            group = get_object_or_404(UserGroups, id=group_id)
            if user.pk != group.owner.pk:
                try:
                    with transaction.atomic(using="default"):
                        with db.transaction:
                            group.users.remove(user)
                            remove_perm('can_publish', user, group)
                    return HttpResponse(json.dumps("user_unfollow"), content_type='application/javascript')
                except (ObjectDoesNotExist, IntegrityError) as e:
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
                                      id=group_id)
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        like, created = LikeGroup.objects.get_or_create(
                            from_like=user, to_like=group)
            except (IntegrityError, ObjectDoesNotExist) as e:
                logging.info(e)
                return JsonResponse({'response': 'error'})

            if not created:
                try:
                    like.delete()
                    NodeGroup.nodes.get(group_id=group.id).likes.disconnect(
                        NodeProfile.nodes.get(user_id=user.id))
                except IntegrityError as e:
                    return JsonResponse({'response': 'error'})
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
    paginate_by = 25

    def __init__(self, *args, **kwargs):
        super(FollowersGroup, self).__init__(*args, **kwargs)
        self.group = None

    @method_decorator(user_can_view_group_info)
    def dispatch(self, request, *args, **kwargs):
        return super(FollowersGroup, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.group = UserGroups.objects.get(slug=self.kwargs['groupname'])
        return self.group.users.all()

    def get_context_data(self, **kwargs):
        context = super(FollowersGroup, self).get_context_data(**kwargs)
        user = self.request.user
        context['group'] = self.group
        context['enable_kick_btn'] = user.has_perm('kick_member', self.group)
        return context


class LikeListGroup(ListView):
    """
    Vista con los usuarios que han dado like a un grupo
    """
    context_object_name = 'like_list'
    template_name = 'groups/user_likes.html'
    paginate_by = 25

    def __init__(self, *args, **kwargs):
        super(LikeListGroup, self).__init__(*args, **kwargs)
        self.group = None

    @method_decorator(user_can_view_group_info)
    def dispatch(self, request, *args, **kwargs):
        return super(LikeListGroup, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.group = UserGroups.objects.get(slug=self.kwargs.pop('groupname', None))
        return LikeGroup.objects.filter(to_like_id=self.group.id).values('from_like__username',
                                                                         'from_like__first_name',
                                                                         'from_like__last_name',
                                                                         'from_like__profile__back_image'
                                                                         )

    def get_context_data(self, **kwargs):
        context = super(LikeListGroup, self).get_context_data(**kwargs)
        context['group'] = self.group
        return context


likes_group = login_required(LikeListGroup.as_view(), login_url='/')


class RespondGroupRequest(View):
    http_method_names = ['post', ]

    def post(self, request, **kwargs):
        user = request.user
        request_id = int(request.POST.get('slug', None))
        request_status = request.POST.get('status', None)
        response = 'error'
        try:
            request_group = RequestGroup.objects.select_related('emitter').get(id=request_id)
            group = UserGroups.objects.get(id=request_group.receiver_id)
        except ObjectDoesNotExist:
            return JsonResponse({'response': response})

        if request_status == 'accept':
            if user.id == group.owner_id:
                try:
                    g = NodeGroup.nodes.get(group_id=group.id)
                    n = NodeProfile.nodes.get(user_id=request_group.emitter_id)
                except (NodeGroup.DoesNotExist, NodeProfile.DoesNotExist) as e:
                    return JsonResponse({'response': response})
                try:
                    with transaction.atomic(using="default"):
                        with db.transaction:
                            request_group.delete()
                            group.users.add(user)
                            g.members.connect(n)
                            notify.send(user, actor=user.username,
                                        recipient=request_group.emitter,
                                        description="@{0} ha aceptado tu solicitud, ahora eres miembro de {1}.".format(
                                            user.username, group.name
                                        ),
                                        verb=u'¡ahora eres miembro de <a href="/group/%s">%s</a>!.' % (
                                            group.name, group.name),
                                        level='new_member_group')
                except Exception as e:
                    return JsonResponse({'response': 'error'})

                response = "added_friend"

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
    http_method_names = ['post', ]

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
    http_method_names = ['post', ]

    def post(self, request, **kwargs):
        user = request.user
        response = 'error'
        user_id = int(request.POST.get('id', None))
        group_id = int(request.POST.get('group_id', None))

        try:
            group = UserGroups.objects.get(id=group_id)
            user_to_kick = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({'response': 'error'})

        if user.id == user_id or user_id == group.owner_id:
            return JsonResponse({'response': 'is_owner'})

        if user.has_perm('kick_member', group):
            with transaction.atomic(using="default"):
                with db.transaction:
                    group.users.remove(user_to_kick)

            response = 'kicked'

        return JsonResponse({'response': response})


kick_member = login_required(KickMemberGroup.as_view(), login_url='/')


class ProfileGroups(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "groups/list_group_profile.html"
    pagination_class = 'rest_framework.pagination.CursorPagination'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs.pop('user_id'))

        try:
            profile = Profile.objects.get(user_id=user.id)
            request_user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            raise Http404

        privacity = profile.is_visible(request_user)
        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        queryset = UserGroups.objects.filter(id__in=user.user_groups.all()).annotate(members=Count('users')) \
            .order_by('-created')

        paginator = Paginator(queryset, 12)  # Show 25 contacts per page

        page = request.GET.get('page', 1)
        try:
            groups = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            groups = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            groups = paginator.page(paginator.num_pages)

        return Response({'groups': groups, 'profile_id': user.id})


list_group_profile = login_required(ProfileGroups.as_view(), login_url='/')


class CreateGroupThemeView(AjaxableResponseMixin, CreateView):
    form_class = GroupThemeForm
    success_url = '/'
    http_method_names = [u'post']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateGroupThemeView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form, msg=None):
        instance = form.save(commit=False)
        instance.owner = self.request.user
        board_group = form.cleaned_data['board_group']
        try:
            group = UserGroups.objects.get(id=board_group.id)
        except ObjectDoesNotExist:
            raise Http404

        if not group.is_public:
            is_member = self.request.user.user_groups.filter(id=board_group.id).exists()
            if not is_member:
                return super(CreateGroupThemeView, self).form_invalid(form)
            else:
                return super(CreateGroupThemeView, self).form_valid(form)
        else:
            return super(CreateGroupThemeView, self).form_valid(form)


class AddLikeTheme(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddLikeTheme, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = {
            'response': False,
            'status': None,
            'in_hate': False
        }
        try:
            theme = GroupTheme.objects.select_related('board_group').get(id=request.POST['pk'])
        except ObjectDoesNotExist:
            raise Http404

        group = UserGroups.objects.get(id=theme.board_group_id)

        if not group.is_public:
            is_member = user.user_groups.filter(id=theme.board_group_id).exists()
            if not is_member:
                return HttpResponseForbidden()

        try:
            with transaction.atomic(using='default'):
                count, row = HateGroupTheme.objects.filter(theme=theme, by_user=user).delete()
                obj, created = LikeGroupTheme.objects.get_or_create(theme=theme, by_user=user)
            if count > 0:
                data['in_hate'] = True
        except IntegrityError:
            return JsonResponse(data)

        if not created:
            try:
                obj.delete()
            except IntegrityError:
                return JsonResponse(data)
            data['status'] = 1
        else:
            data['status'] = 2

        data['response'] = True

        return JsonResponse(data)


class AddHateTheme(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddHateTheme, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = {
            'response': False,
            'status': None,
            'in_like': False
        }
        try:
            theme = GroupTheme.objects.select_related('board_group').get(id=request.POST['pk'])
        except ObjectDoesNotExist:
            raise Http404

        group = UserGroups.objects.get(id=theme.board_group_id)

        if not group.is_public:
            is_member = user.user_groups.filter(id=theme.board_group_id).exists()
            if not is_member:
                return HttpResponseForbidden()

        try:
            with transaction.atomic(using='default'):
                count, row = LikeGroupTheme.objects.filter(theme=theme, by_user=user).delete()
                obj, created = HateGroupTheme.objects.get_or_create(theme=theme, by_user=user)
            if count > 0:
                data['in_like'] = True
        except IntegrityError:
            return JsonResponse(data)

        if not created:
            try:
                obj.delete()
            except IntegrityError:
                return JsonResponse(data)
            data['status'] = 1
        else:
            data['status'] = 2

        data['response'] = True

        return JsonResponse(data)


class GroupThemeView(DetailView):
    template_name = 'groups/board_theme.html'

    def get_queryset(self):
        user = self.request.user

        if self.request.is_ajax():
            return GroupTheme.objects.filter(slug=self.kwargs['slug'])

        return GroupTheme.objects.filter(slug=self.kwargs['slug']).annotate(
            likes=Count('like_theme', distinct=True),
            hates=Count('hate_theme', distinct=True)).annotate(
            have_like=Count(Case(
                When(like_theme__by_user_id=user.id, then=Value(1)),
                output_field=IntegerField()
            ))).annotate(have_hate=Count(Case(
            When(hate_theme__by_user_id=user.id, then=Value(1)),
            output_field=IntegerField()
        ))).select_related('owner', 'board_group')

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(GroupThemeView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)

        publications = PublicationTheme.objects.annotate(likes=Count('user_give_me_like'),
                                                         hates=Count('user_give_me_hate'), have_like=Count(Case(
                When(user_give_me_like__id=user.id, then=Value(1)),
                output_field=IntegerField()
            )), have_hate=Count(Case(
                When(user_give_me_hate__id=user.id, then=Value(1)),
                output_field=IntegerField()
            ))).filter(board_theme=self.object,
                       deleted=False).select_related('author', 'board_theme', 'parent', 'parent__author')

        paginator = Paginator(publications, 25)

        try:
            pubs = paginator.page(page)
        except PageNotAnInteger:
            pubs = paginator.page(1)
        except EmptyPage:
            pubs = paginator.page(paginator.num_pages)

        context['publications'] = pubs
        context['form'] = PublicationThemeForm()
        context['group_owner_id'] = UserGroups.objects.values_list('owner_id', flat=True).get(
            id=self.object.board_group_id)
        context['edit_form'] = EditGroupThemeForm(instance=self.object, initial={'pk': self.object.pk})
        return context


class DeleteGroupTheme(DeleteView):
    http_method_names = ['post']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteGroupTheme, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return GroupTheme.objects.get(id=self.request.POST.get('pk'))

    def delete(self, request, *args, **kwargs):
        user = request.user

        data = {
            'response': False,
            'redirect_url': None
        }

        self.object = self.get_object()

        group = UserGroups.objects.get(id=self.object.board_group_id)

        if self.object.owner_id != user.id and (
                        user != group.owner_id and not user.has_perm('delete_publication', group)):
            return JsonResponse(data)

        data['redirect_url'] = reverse('user_groups:group-profile', kwargs={'groupname': group.slug})

        try:
            self.object.delete()
        except IntegrityError:
            pass

        data['response'] = True

        return JsonResponse(data)


class EditPublicationTheme(UpdateView):
    form_class = EditGroupThemeForm
    model = GroupTheme

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditPublicationTheme, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, msg=None):
        user = self.request.user
        data = {
            'response': False,
            'url': None
        }
        theme = GroupTheme.objects.get(id=form.cleaned_data['pk'])

        if theme.owner_id != user.id:
            return HttpResponseForbidden()

        theme.title = form.cleaned_data['title']
        theme.description = form.cleaned_data['description']
        theme.image = form.cleaned_data['image']

        theme.save()

        data['url'] = reverse_lazy('user_groups:group_theme', kwargs={'slug': theme.slug})
        return JsonResponse(data)

    def form_invalid(self, form):

        super(EditPublicationTheme, self).form_invalid(form)
        return JsonResponse({'response': False})
