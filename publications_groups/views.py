from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.views.generic.list import ListView

from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from emoji.models import Emoji
from publications.exceptions import EmptyContent
from publications.models import Publication
from publications.views import logger
from publications_groups.forms import PublicationGroupForm
from publications.forms import SharedPublicationForm
from publications_groups.models import PublicationGroup
from user_groups.models import UserGroups, NodeGroup
from user_profile.models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .utils import optimize_publication_media
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q


@method_decorator(login_required, name='dispatch')
class PublicationGroupView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para una imagen de
    la galeria de un usuario.
    """
    form_class = PublicationGroupForm
    model = PublicationGroup
    http_method_names = [u'post']
    success_url = '/thanks/'

    def __init__(self):
        self.object = None
        super(PublicationGroupView, self).__init__()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        group = get_object_or_404(UserGroups, id=request.POST.get('board_group', None))
        emitter = User.objects.get(id=self.request.user.id)

        try:
            emitter_node = NodeProfile.nodes.get(user_id=emitter.id)
            group_node = NodeGroup.nodes.get(group_id=group.group_ptr_id)
        except (NodeProfile.DoesNotExist, NodeGroup.DoesNotExist) as e:
            raise Http404

        if group.owner.id != emitter.id:
            if not group.is_public and not group_node.members.is_connected(emitter_node):
                return self.form_invalid(form=form)

        is_correct_content = False

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author_id = emitter.id
                publication.board_group_id = group.id
                parent = publication.parent
                if parent:
                    author = NodeProfile.nodes.get(user_id=parent.author_id)

                    if author.bloq.is_connected(emitter_node):
                        raise PermissionDenied('El autor de la publicación te ha bloqueado')

                soup = BeautifulSoup(publication.content)  # Buscamos si entre los tags hay contenido
                for tag in soup.find_all(recursive=True):
                    if tag.text and not tag.text.isspace():
                        is_correct_content = True
                        break

                if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion

                    logger.info('Publicacion contiene espacios o no tiene texto')
                    raise EmptyContent('¡Comprueba el texto del comentario!')

                if publication.content.isspace():  # Comprobamos si el comentario esta vacio
                    raise EmptyContent('¡Comprueba el texto del comentario!')

                publication.parse_mentions()  # add mentions
                publication.parse_content()  # parse publication content
                publication.add_hashtag()  # add hashtags
                publication.content = Emoji.replace(publication.content)  # Add emoji img

                media = request.FILES.getlist('image')

                try:
                    with transaction.atomic(using="default"):
                        publication.save()  # Creamos publicacion
                        form.save_m2m()  # Saving tags
                        transaction.on_commit(
                            lambda: optimize_publication_media(publication, media))
                        transaction.on_commit(lambda: publication.send_notification(request, is_edited=False))
                except Exception as e:
                    raise ValidationError(e)

                if not media:
                    return self.form_valid(form=form)
                else:
                    return self.form_valid(form=form,
                                           msg=u"Estamos procesando tus videos, te avisamos "
                                               u"cuando la publicación esté lista.")
            except Exception as e:
                logger.info("Publication not created -> {}".format(e))
                return self.form_invalid(form=form, errors=e)
        return self.form_invalid(form=form)


publication_group_view = login_required(PublicationGroupView.as_view(), login_url='/')


class DeletePublication(View):
    http_method_names = ['post', ]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, **kwargs):
        user = request.user
        pub_id = request.POST.get('id', None)
        board_group_id = request.POST.get('board_group', None)
        response = 'error'

        if not pub_id or not board_group_id:
            return JsonResponse({'response': response})

        try:
            group = UserGroups.objects.get(group_ptr_id=board_group_id)
            publication = PublicationGroup.objects.get(id=pub_id, board_group_id=board_group_id)
        except ObjectDoesNotExist:
            return JsonResponse({'response': response})

        if publication.author_id == user.id or user.has_perm('delete_publication', group):
            try:
                with transaction.atomic(using="default"):
                    publication.deleted = True
                    publication.save(update_fields=['deleted'])
                    publication.get_descendants().update(deleted=True)
            except Exception as e:
                logger.info(e)
                return JsonResponse({'response': response})
            response = True
        return JsonResponse({'response': response})


delete_publication = login_required(DeletePublication.as_view(), login_url='/')


class AddPublicationLike(View):
    """
    Clase para dar me gusta a un comentario
    """
    model = PublicationGroup

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddPublicationLike, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        pub_id = request.POST.get('pk', None)

        if not user.is_authenticated:
            return HttpResponseForbidden()

        if not pub_id:
            raise Http404

        try:
            publication = PublicationGroup.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            raise Http404

        try:
            author = NodeProfile.nodes.get(user_id=publication.author_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponseForbidden()

        privacity = author.is_visible(m)

        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        in_like = False
        in_hate = False

        if publication.user_give_me_like.filter(pk=user.pk).exists():  # Usuario en lista de likes
            in_like = True

        if publication.user_give_me_hate.filter(pk=user.pk).exists():  # Usuario en lista de hate
            in_hate = True

        if in_like and in_hate:  # Si esta en ambas listas (situacion no posible)
            publication.user_give_me_like.remove(user)
            publication.user_give_me_hate.remove(user)
            logger.info("Usuario esta en ambas listas, eliminado usuario de ambas listas")

        if in_hate:  # Si ha dado antes unlike
            logger.info("Incrementando like")
            logger.info("Decrementando hate")
            try:
                publication.user_give_me_hate.remove(user)  # remove from hates
                publication.user_give_me_like.add(user)  # add to like
                publication.save()
                response = True
                statuslike = 3

            except IntegrityError:
                response = False
                statuslike = 0

        elif in_like:  # Si ha dado antes like
            logger.info("Decrementando like")
            try:
                publication.user_give_me_like.remove(request.user)
                publication.save()
                response = True
                statuslike = 2
            except IntegrityError:
                response = False
                statuslike = 0

        else:  # Si no ha dado like ni unlike
            try:
                publication.user_give_me_like.add(user)
                publication.save()
                response = True
                statuslike = 1
            except IntegrityError:
                response = False
                statuslike = 0

        data = {'response': response, 'statuslike': statuslike}
        return JsonResponse(data)


class AddPublicationHate(View):
    """
    Clase para dar me gusta a un comentario
    """
    model = PublicationGroup

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddPublicationHate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        pub_id = request.POST.get('pk', None)

        if not user.is_authenticated:
            return HttpResponseForbidden()

        if not pub_id:
            raise Http404

        try:
            publication = PublicationGroup.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            raise Http404

        try:
            author = NodeProfile.nodes.get(user_id=publication.author_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponseForbidden()

        privacity = author.is_visible(m)

        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        in_like = False
        in_hate = False

        if publication.user_give_me_like.filter(pk=user.pk).exists():  # Usuario en lista de likes
            in_like = True

        if publication.user_give_me_hate.filter(pk=user.pk).exists():  # Usuario en lista de hate
            in_hate = True

        if in_like and in_hate:  # Si esta en ambas listas (situacion no posible)
            publication.user_give_me_like.remove(user)
            publication.user_give_me_hate.remove(user)
            logger.info("Usuario esta en ambas listas, eliminado usuario de ambas listas")

        if in_like:  # Si ha dado antes like
            logger.info("Incrementando hate")
            logger.info("Decrementando like")
            try:
                publication.user_give_me_like.remove(user)  # remove from like
                publication.user_give_me_hate.add(user)  # add to hate
                publication.save()
                response = True
                status_like = 3

            except IntegrityError as e:
                response = False
                status_like = 0

        elif in_hate:  # Si ha dado antes hate
            logger.info("Decrementando hate")
            try:
                publication.user_give_me_hate.remove(request.user)
                publication.save()
                response = True
                status_like = 2
            except IntegrityError as e:
                response = False
                status_like = 0

        else:  # Si no ha dado like ni unlike
            try:
                publication.user_give_me_hate.add(user)
                publication.save()
                response = True
                status_like = 1
            except IntegrityError as e:
                response = False
                status_like = 0

        data = {'response': response, 'statuslike': status_like}
        return JsonResponse(data)


class EditGroupPublication(UpdateView):
    model = PublicationGroup
    fields = ['content', ]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditGroupPublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = {'response': False}
        content = request.POST.get('content', None)
        pub_id = request.POST.get('id', None)

        try:
            publication = PublicationGroup.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            raise Http404

        if publication.author.id != user.id:
            return HttpResponseForbidden()

        is_correct_content = False
        soup = BeautifulSoup(publication.content)  # Buscamos si entre los tags hay contenido
        for tag in soup.find_all(recursive=True):
            if tag.text and not tag.text.isspace():
                is_correct_content = True
                break

        if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion
            logger.info('Publicacion contiene espacios o no tiene texto')
            raise IntegrityError('El comentario esta vacio')

        if publication.content.isspace():  # Comprobamos si el comentario esta vacio
            raise IntegrityError('El comentario esta vacio')

        try:
            publication.add_hashtag()
            publication.parse_content()
            publication.parse_mentions()
            publication.content = Emoji.replace(content)
            publication.save(update_fields=['content'])  # Guardamos la publicacion si no hay errores
            publication.send_notification(request, is_edited=True)
            data['response'] = True
        except IntegrityError:
            pass

        return JsonResponse(data)


class PublicationGroupDetail(ListView):
    model = PublicationGroup
    template_name = 'groups/publication_detail.html'

    def __init__(self, **kwargs):
        super(PublicationGroupDetail).__init__(**kwargs)
        self.publication = None
        self.shared_pubs = {}
        self.pubs_shared_with_me = []

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PublicationGroupDetail, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        pub_id = self.kwargs.get('pk', None)
        page = self.request.GET.get('page', 1)
        user = self.request.user

        try:
            self.publication = PublicationGroup.objects.select_related('board_group').get(id=pub_id, deleted=False)
        except ObjectDoesNotExist:
            raise Http404

        try:
            n = NodeProfile.nodes.get(user_id=self.request.user.id)
            g = NodeGroup.nodes.get(group_id=self.publication.board_group.group_ptr_id)
        except (NodeProfile.DoesNotExist, NodeGroup.DoesNotExist) as e:
            raise Http404

        if not self.publication.board_group.is_public and not g.members.is_connected(n):
            return HttpResponseForbidden()

        publications = self.publication.get_descendants(include_self=True) \
            .filter(deleted=False) \
            .prefetch_related('group_extra_content', 'images',
                              'videos', 'user_give_me_like', 'user_give_me_hate', 'tags') \
            .select_related('author',
                            'board_group',
                            'parent')

        paginator = Paginator(publications, 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        self.shared_pubs = {item['shared_group_publication__id']: item.get('total', 0) for item in
                            (Publication.objects.filter(shared_group_publication__id__in=(
                                publications.object_list.values_list('id', flat=True)), deleted=False).values(
                                'shared_group_publication__id') \
                             .order_by('shared_group_publication__id') \
                             .annotate(total=Count('shared_group_publication__id')))}

        self.pubs_shared_with_me = Publication.objects.filter(shared_group_publication__id__in=(
            publications.object_list.values_list('id', flat=True)),
            author__id=user.id,
            deleted=False).values_list('shared_group_publication__id',
                                       flat=True)
        return publications

    def get_context_data(self, **kwargs):
        context = super(PublicationGroupDetail, self).get_context_data(**kwargs)
        if not self.request.is_ajax():
            context['publication_id'] = self.kwargs.get('pk', None)
            context['share_publication'] = SharedPublicationForm()
        context['group_profile'] = self.publication.board_group
        context['pubs_shared'] = self.shared_pubs
        context['pubs_shared_with_me'] = self.pubs_shared_with_me
        return context


class LoadRepliesForPublicationGroup(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoadRepliesForPublicationGroup, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return JsonResponse({'error': 'error'})

        user = request.user
        pub_id = request.GET.get('pubid', None)
        page = request.GET.get('page', 1)

        try:
            publication = PublicationGroup.objects.select_related('board_group').get(id=pub_id)
        except ObjectDoesNotExist:
            raise Http404

        try:
            group = UserGroups.objects.get(group_ptr_id=publication.board_group.group_ptr_id)
        except ObjectDoesNotExist:
            raise Http404

        if group.is_public:
            pass
        else:
            try:
                g = NodeGroup.nodes.get(group_id=publication.board_group.group_ptr_id)
            except NodeGroup.DoesNotExist:
                raise Http404
            try:
                n = NodeProfile.nodes.get(user_id=user.id)
            except NodeProfile.DoesNotExist:
                raise Http404
            if not g.members.is_connected(n):
                return HttpResponseForbidden()

        if not publication.parent:
            pubs = publication.get_descendants() \
                .filter(~Q(author__profile__from_blocked__to_blocked=user.profile)
                        & Q(level__lte=1) & Q(deleted=False))

        else:
            pubs = publication.get_descendants() \
                .filter(
                ~Q(author__profile__from_blocked__to_blocked=user.profile)
                & Q(deleted=False))

        pubs = pubs.prefetch_related('group_extra_content', 'images',
                                     'videos', 'user_give_me_like', 'user_give_me_hate', 'tags') \
            .select_related('author',
                            'board_group',
                            'parent')

        paginator = Paginator(pubs, 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        shared_id = publications.object_list.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_group_publication__id__in=shared_id, deleted=False).values(
            'shared_group_publication__id') \
            .order_by('shared_group_publication__id') \
            .annotate(total=Count('shared_group_publication__id'))
        shared_pubs = {item['shared_group_publication__id']: item.get('total', 0) for item in pubs_shared}

        pubs_shared_with_me = Publication.objects.filter(shared_group_publication__id__in=shared_id, author__id=user.id,
                                                         deleted=False).values_list('shared_group_publication__id',
                                                                                    flat=True)

        try:
            page = publications.next_page_number()
        except EmptyPage:
            page = None

        data = {
            'content': render_to_string(request=request, template_name='groups/ajax_load_group_replies.html',
                                        context={'publications': publications, 'group_profile': group,
                                                 'pubs_shared': shared_pubs,
                                                 'pubs_shared_with_me': pubs_shared_with_me}),
            'page': page,
            'childs': len(publications),

        }

        return JsonResponse(data)


xstr = lambda s: s or ""


class ShareGroupPublication(View):
    def post(self, request, *args, **kwargs):
        form = SharedPublicationForm(request.POST or None)

        if form.is_valid():
            data = {}
            user = request.user
            pub_id = form.cleaned_data['pk']
            try:
                pub_to_add = PublicationGroup.objects.get(id=pub_id)
            except ObjectDoesNotExist:
                raise Http404

            try:
                author = NodeProfile.nodes.get(user_id=pub_to_add.author_id)
                m = NodeProfile.nodes.get(user_id=user.id)
            except NodeProfile.DoesNotExist:
                raise Http404

            privacity = author.is_visible(m)

            if privacity and privacity != 'all':
                return HttpResponseForbidden()

            shared = Publication.objects.filter(shared_group_publication=pub_id, author_id=user.id,
                                                deleted=False).exists()

            if not shared:
                content = form.cleaned_data.get('content', None)
                try:
                    pub = Publication.objects.create(
                        content='<i class="material-icons blue1e88e5 left">format_quote</i> Ha compartido de <a '
                                'href="/profile/%s">@%s</a><br>%s' % (
                                    pub_to_add.author.username, pub_to_add.author.username, content),
                        shared_group_publication=pub_to_add,
                        author=user,
                        board_owner=user, event_type=6)
                    pub.send_notification(request)
                    data['response'] = True
                except IntegrityError:
                    pass

            return JsonResponse(data)


class RemoveSharedGroupPublication(View):
    model = Publication

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RemoveSharedGroupPublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk', None)
        user = request.user
        try:
            Publication.objects.filter(shared_group_publication_id=pk, author_id=user.id).delete()
        except ObjectDoesNotExist:
            raise Http404
        data = {
            'response': True,
        }
        return JsonResponse(data)
