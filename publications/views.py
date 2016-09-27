import json
from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from text_processor.format_text import TextProcessor
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from publications.forms import PublicationForm
from publications.models import Publication
from timeline.models import Timeline
from notifications.signals import notify


class PublicationNewView(AjaxableResponseMixin, CreateView):
    form_class = PublicationForm
    model = Publication
    http_method_names = [u'post']
    success_url = '/thanks/'

    def post(self, request, *args, **kwargs):
        # self.object = None
        # form = PublicationForm(request.POST)
        form = self.get_form()
        emitter = get_object_or_404(get_user_model(),
                                    pk=request.POST['author'])
        board_owner = get_object_or_404(get_user_model(),
                                        pk=request.POST['board_owner'])
        publication = None
        print('POST DATA: {}'.format(request.POST))
        print('tipo emitter: {}'.format(type(emitter)))
        print('tipo board_owner: {}'.format(type(board_owner)))
        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author = emitter
                publication.board_owner = board_owner
                if publication.content.isspace():
                    raise IntegrityError('El comentario esta vacio')
                publication.save(new_comment=True)
                print('>>>> PUBLICATION: ')
                t, created = Timeline.objects.get_or_create(publication=publication, author=publication.author.profile,
                                                            profile=publication.board_owner.profile)
                return self.form_valid(form=form)
            except IntegrityError as e:
                print("views.py line 48 -> {}".format(e))

        return self.form_invalid(form=form)


class PublicationsListView(AjaxableResponseMixin, ListView):
    model = Publication
    template_name = 'account/tab-comentarios.html'
    http_method_names = ['get']
    ordering = ['-created']
    allow_empty = True
    context_object_name = 'publication_list'
    paginate_by = 1
    queryset = Publication.objects.all()

    def get_queryset(self):
        print(self.request.GET.get('type'))
        if self.request.GET.get('type') == 'reply':
            # TODO: pasar el resto de parametros por get
            self.template_name = 'account/tab-comentarios.html'
            return Publication.objects.get_publication_replies(
                                        self.request.GET.get('user_pk'),
                                        self.request.GET.get('booar_owner'),
                                        self.request.GET.get('parent'))
        else:
            return self.queryset


'''def publication_form(request):
    print('>>>>>>>> PETICION AJAX PUBLICACION')
    if request.POST:
        form = PublicationForm(request.POST)
        userprofile = get_object_or_404(get_user_model(), pk=request.POST['userprofileid'])
        emitter = get_object_or_404(get_user_model(), pk=request.POST['emitterid'])
        response = False
        publication = None

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author = emitter.profile
                publication.profile = userprofile.profile
                if publication.content.isspace():
                    raise IntegrityError('El comentario esta vacio')
                publication.content = TextProcessor.get_format_text(publication.content, emitter)
                print(str(userprofile.profile))
                print(str(emitter.profile))
                """ Send notification to userprofile """
                if userprofile.pk != emitter.pk:
                    notify.send(emitter, actor=emitter.username, recipient=userprofile, verb=u'¡ha publicado un comentario en tu tablón!', description="Contenido: " + publication.content)
                publication.save()
                response = True
            except IntegrityError:
                pass

        jsons = json.dumps({'response': response})
        return HttpResponse(jsons, content_type='application/json')'''


def delete_publication(request):
    print('>>>>>>>> PETICION AJAX BORRAR PUBLICACION')
    if request.POST:
        # print request.POST['userprofile_id']
        # print request.POST['publication_id']
        obj_userprofile = get_object_or_404(
            get_user_model(),
            pk=request.POST['userprofile_id']
        )
        print(obj_userprofile)
        try:
            obj_userprofile.profile.remove_publication(
                publicationid=request.POST['publication_id']
            )
            try:
                t = Timeline.objects.get(publication__pk=request.POST['publication_id']).delete()
            except ObjectDoesNotExist:
                pass

            response = True
        except ObjectDoesNotExist:
            response = False

        return HttpResponse(json.dumps(response),
                            content_type='application/json'
                            )


def load_publications(request):
    global publications_next
    print('>>>>>> PETICION AJAX, CARGAR MAS PUBLICACIONES')
    publicationslist = request.session.get('publications_list', None)
    if publicationslist == None:
        publications_next = None
    else:
        publicationslist = json.loads(publicationslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            print('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 15
            publications_next = publicationslist[n - 15:n]
            print('>>>>>>> LISTA: ')
            print(publications_next)

    return HttpResponse(json.dumps(list(publications_next)), content_type='application/json')

def add_like(request):
    response = False
    statuslike = 0
    data = []
    if request.POST:
        id_for_publication = request.POST['publication_id']  # Obtenemos el ID de la publicacion
        pub = Publication.objects.get(id=id_for_publication)  # Obtenemos la publicacion
        # que vamos a incrementar sus likes
        user_profile = get_object_or_404(
            get_user_model(),
            pk=pub.author.id
        )

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        print("(USUARIO PETICIÓN): " + request.user.username + " PK_ID -> " + str(request.user.pk))
        print("(PERFIL DE USUARIO): " + user_profile.username + " PK_ID -> " + str(user_profile.pk))
        print("(USERS QUE HICIERON LIKE): ")
        print(pub.user_give_me_like.all())

        if request.user.pk != user_profile.pk and not request.user in pub.user_give_me_like.all()\
                and not request.user in pub.user_give_me_hate.all():
            # Si el escritor del comentario
            # es el que pulsa el boton de like
            # no dejamos que incremente el contador
            # tampoco si el usuario ya ha dado like antes.
            print ("Incrementando like")
            try:
                pub.user_give_me_like.add(request.user) # add users like
                pub.save()
                response = True
                statuslike = 1

            except ObjectDoesNotExist:
                response = False
                statuslike = 0
        elif request.user.pk != user_profile.pk and request.user in pub.user_give_me_like.all()\
                and not request.user in pub.user_give_me_hate.all():
            print ("Decrementando like")
            try:
                pub.user_give_me_like.remove(request.user)
                pub.save()
                response = True
                statuslike = 2
            except ObjectDoesNotExist:
                response = False
                statuslike = 0
        else:
            response = False
            statuslike = 0
    print("Fin like comentario ---> Response" + str(response)
    + " Estado" + str(statuslike))
    data = json.dumps({'response': response, 'statuslike': statuslike})
    return HttpResponse(data, content_type='application/json')

def add_hate(request):
    response = False
    statuslike = 0
    data = []
    if request.POST:
        id_for_publication = request.POST['publication_id']  # Obtenemos el ID de la publicacion
        pub = Publication.objects.get(id=id_for_publication)  # Obtenemos la publicacion
        # que vamos a incrementar sus likes
        user_profile = get_object_or_404(
            get_user_model(),
            pk=pub.author.id
        )

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        print("(USUARIO PETICIÓN): " + request.user.username)
        print("(PERFIL DE USUARIO): " + user_profile.username)
        print("(USERS QUE HICIERON LIKE): ")
        print(pub.user_give_me_hate.all())

        if request.user.pk != user_profile.pk and request.user not in pub.user_give_me_like.all()\
                and request.user not in pub.user_give_me_hate.all():
            # Si el escritor del comentario
            # es el que pulsa el boton de like
            # no dejamos que incremente el contador
            # tampoco si el usuario ya ha dado like antes.
            print ("Incrementando like")
            try:
                pub.user_give_me_hate.add(request.user) # add users like
                pub.save()
                response = True
                statuslike = 1

            except ObjectDoesNotExist:
                response = False
                statuslike = 0
        elif request.user.pk != user_profile.pk and request.user in pub.user_give_me_hate.all()\
                and not request.user in pub.user_give_me_like.all():
            print ("Decrementando like")
            try:
                pub.user_give_me_hate.remove(request.user)
                pub.save()
                response = True
                statuslike = 2
            except ObjectDoesNotExist:
                response = False
                statuslike = 0
        else:
            response = False
            statuslike = 0
    print("Fin like comentario ---> Response" + str(response)
    + " Estado" + str(statuslike))
    data = json.dumps({'response': response, 'statuslike': statuslike})
    return HttpResponse(data, content_type='application/json')
