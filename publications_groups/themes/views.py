import magic
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView

from emoji import Emoji
from publications.exceptions import MaxFilesReached, SizeIncorrect, MediaNotSupported, CantOpenMedia
from publications_groups.forms import PublicationThemeForm, ThemePublicationEdit
from publications_groups.themes.models import PublicationTheme
from publications_groups.themes.utils import optimize_publication_media, check_image_property
from publications_groups.utils import check_num_images
from user_groups.models import GroupTheme, UserGroups
from user_profile.node_models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin


class PublicationThemeView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para una imagen de
    la galeria de un usuario.
    """
    form_class = PublicationThemeForm
    model = PublicationTheme

    def __init__(self):
        self.object = None
        super(PublicationThemeView, self).__init__()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PublicationThemeView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('user_profile:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form, msg=None):
        user = self.request.user
        form.instance.author = user

        try:
            group_id = GroupTheme.objects.values_list('board_group_id', flat=True).get(id=form.instance.board_theme.id)
            group = UserGroups.objects.get(id=group_id)
        except ObjectDoesNotExist:
            form.add_error('board_theme', 'El tema especificado no existe.')
            return super(PublicationThemeView, self).form_invalid(form)

        if not group.is_public and not user.user_groups.filter(id=group_id).exists():
            form.add_error('board_theme',
                           'Para comentar en este tema debes ser miembro del grupo {0}.'.format(group.name))
            return super(PublicationThemeView, self).form_invalid(form)

        if form.instance.parent:
            try:
                author = NodeProfile.nodes.get(user_id=form.instance.parent.author_id)
                emitter_node = NodeProfile.nodes.get(user_id=user.id)
            except NodeProfile.DoesNotExist:
                raise Http404

            if author.bloq.is_connected(emitter_node):
                form.add_error('parent',
                               'El autor de la publicación te ha bloqueado.'.format(group.name))
                return super(PublicationThemeView, self).form_invalid(form)

        media = self.request.FILES.getlist('image')

        try:
            check_num_images(media)
        except MaxFilesReached:
            form.add_error('content', 'El número máximo de imágenes que puedes subir es 5.')
            return self.form_invalid(form=form)

        for file in media:
            check_image_property(file)

        try:
            exts = [magic.from_buffer(x.read(), mime=True).split('/') for x in media]
        except magic.MagicException as e:
            form.add_error('content', 'No hemos podido procesar los archivos adjuntos.')
            return self.form_invalid(form=form)

        have_video = False
        if any(word in 'gif video' for word in set([item for sublist in exts for item in sublist])):
            have_video = True

        try:
            with transaction.atomic(using="default"):
                form.instance.parse_content()
                form.instance.parse_mentions()
                form.instance.add_hashtag()
                if not have_video:
                    saved = super(PublicationThemeView, self).form_valid(form)
                else:
                    saved = super(PublicationThemeView, self).form_valid(form,
                                                                         msg=u"Estamos procesando tus videos, te avisamos "
                                                                             u"cuando la publicación esté lista.")
                transaction.on_commit(
                    lambda: optimize_publication_media(form.instance, media, exts))
                transaction.on_commit(lambda: form.instance.send_notification(self.request))

        except (SizeIncorrect, MediaNotSupported, CantOpenMedia) as ex:
            form.add_error('content', str(ex))
            form.instance.delete()
            return self.form_invalid(form=form)

        except IntegrityError as e:
            form.add_error('content', str(e))
            return self.form_invalid(form=form)

        return saved


class AddLikePublicationTheme(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddLikePublicationTheme, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = {
            'response': False,
            'status': None,
            'in_hate': False
        }
        try:
            publication = PublicationTheme.objects.get(id=request.POST['pk'])
        except ObjectDoesNotExist:
            raise Http404

        in_hate = in_like = False
        try:
            with transaction.atomic(using='default'):
                if publication.user_give_me_hate.filter(id=user.id).exists():
                    publication.user_give_me_hate.remove(user)
                    in_hate = True

                if publication.user_give_me_like.filter(id=user.id).exists():
                    in_like = True
                else:
                    publication.user_give_me_like.add(user)

                if in_like:
                    try:
                        publication.user_give_me_like.remove(user)
                    except IntegrityError:
                        return JsonResponse(data)
                    data['status'] = 1
                else:
                    data['status'] = 2

            if in_hate:
                data['in_hate'] = True

        except IntegrityError:
            return JsonResponse(data)

        data['response'] = True

        return JsonResponse(data)


class AddHatePublicationTheme(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddHatePublicationTheme, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = {
            'response': False,
            'status': None,
            'in_like': False
        }
        try:
            publication = PublicationTheme.objects.get(id=request.POST['pk'])
        except ObjectDoesNotExist:
            raise Http404

        in_hate = in_like = False
        try:
            with transaction.atomic(using='default'):
                if publication.user_give_me_like.filter(id=user.id).exists():
                    publication.user_give_me_like.remove(user)
                    in_like = True

                if publication.user_give_me_hate.filter(id=user.id).exists():
                    in_hate = True
                else:
                    publication.user_give_me_hate.add(user)

                if in_hate:
                    try:
                        publication.user_give_me_hate.remove(user)
                    except IntegrityError:
                        return JsonResponse(data)
                    data['status'] = 1
                else:
                    data['status'] = 2

            if in_like:
                data['in_like'] = True

        except IntegrityError:
            return JsonResponse(data)

        data['response'] = True

        return JsonResponse(data)


class DeletePublicationTheme(UpdateView):
    model = PublicationTheme

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePublicationTheme, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(pk=self.request.POST.get('pk'))
        except ObjectDoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        response = False
        self.object = self.get_object()
        if not self.object:
            return JsonResponse({'response': False})

        user = request.user
        group_owner_id = UserGroups.objects.values_list('owner_id', flat=True).get(
            id=self.object.board_theme.board_group_id)

        if self.object.author_id != user.id and user.id != group_owner_id:
            return HttpResponseForbidden()

        self.object.deleted = True
        try:
            self.object.save(update_fields=['deleted'])
            response = True
        except IntegrityError:
            pass

        return JsonResponse({'response': response})


class EditThemePublication(UpdateView):
    model = PublicationTheme
    form_class = ThemePublicationEdit

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditThemePublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = self.request.user
        data = {'response': False}

        content = form.cleaned_data['content']
        pk = form.cleaned_data['pk']

        try:
            publication = PublicationTheme.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise Http404

        if publication.author.id != user.id:
            return HttpResponseForbidden()

        try:
            publication.content = content
            publication.parse_content()
            publication.add_hashtag()
            publication.parse_mentions()
            publication.content = Emoji.replace(publication.content)
            publication._edited = True
            with transaction.atomic(using="default"):
                publication.save(update_fields=['content'])  # Guardamos la publicacion si no hay errores
                transaction.on_commit(lambda: publication.send_notification(self.request, is_edited=True))
            data['response'] = True
        except IntegrityError:
            pass

        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({'response': False})
