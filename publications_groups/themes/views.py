from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView

from publications_groups.forms import PublicationThemeForm
from publications_groups.themes.models import PublicationTheme
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
            group = UserGroups.objects.get(group_ptr_id=group_id)
        except ObjectDoesNotExist:
            form.add_error('board_theme', 'El tema especificado no existe.')
            return super(PublicationThemeView, self).form_invalid(form)

        if not group.is_public and not user.groups.filter(id=group_id).exists():
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

        try:
            with transaction.atomic(using="default"):
                form.instance.parse_content()
                form.instance.parse_mentions()
                form.instance.add_hashtag()
                saved = super(PublicationThemeView, self).form_valid(form)
                transaction.on_commit(lambda: form.instance.send_notification(self.request))
        except IntegrityError:
            raise Exception('Error al guardar la publicacion')

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
        if self.object.author_id != user.id:
            return HttpResponseForbidden()

        self.object.deleted = True
        try:
            self.object.save(update_fields=['deleted'])
            response = True
        except IntegrityError:
            pass

        return JsonResponse({'response': response})