from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, \
    render_to_response, get_object_or_404, render
from django.template import RequestContext, RequestContext, loader
from django.utils import timezone
from django.utils.translation import ugettext as _
from django_messages.forms import ComposeForm
from django_messages.models import Message
from django_messages.utils import format_quote, get_user_model, \
    get_username_field

from user_profile.models import Relationship, LikeProfile, UserProfile
from publications.forms import PublicationForm
from user_profile.forms import SearchForm
import json
import re
User = get_user_model()

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

@login_required(login_url='/')
def inbox(request, template_name='django_messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    user = request.user

    searchForm = SearchForm(request.POST) # Cuadro de búsqueda
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial) # Mostrar formulario para enviar mensajes.

    user_profile = user
     # cargar lista de amigos (12 primeros)
    try:
        #friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends
    message_list = Message.objects.inbox_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list, 'friends_top12': friends_top12,
    'publicationSelfForm' :publicationForm, 'searchForm': searchForm}, context_instance=RequestContext(request))

@login_required(login_url='/')
def outbox(request,template_name='django_messages/outbox.html'):
    """
    Displays a list of sent messages by the current user.
    Optional arguments:
        ``template_name``: name of the template to use.
    """
    user = request.user

    searchForm = SearchForm(request.POST) # Cuadro de búsqueda
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial) # Mostrar formulario para enviar mensajes.

    user_profile = user
     # cargar lista de amigos (12 primeros)
    try:
        #friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends
    message_list = Message.objects.inbox_for(request.user)

    message_list = Message.objects.outbox_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list, 'friends_top12': friends_top12,
'publicationSelfForm': publicationForm, 'searchForm': searchForm}, context_instance=RequestContext(request))

@login_required(login_url='/')
def trash(request,template_name='django_messages/trash.html'):
    """
    Displays a list of deleted messages.
    Optional arguments:
        ``template_name``: name of the template to use
    Hint: A Cron-Job could periodicly clean up old messages, which are deleted
    by sender and recipient.
    """
    user = request.user

    searchForm = SearchForm(request.POST) # Cuadro de búsqueda
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial) # Mostrar formulario para enviar mensajes.

    user_profile = user
     # cargar lista de amigos (12 primeros)
    try:
        #friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends
    message_list = Message.objects.inbox_for(request.user)

    message_list = Message.objects.trash_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list, 'friends_top12' : friends_top12,
'searchForm': searchForm, 'publicationSelfForm': publicationForm}, context_instance=RequestContext(request))

@login_required(login_url='/')
def compose(request,recipient=None, form_class=ComposeForm,
        template_name='django_messages/compose.html', success_url=None, recipient_filter=None):
    """
    Displays and handles the ``form_class`` form to compose new messages.
    Required Arguments: None
    Optional Arguments:
        ``recipient``: username of a `django.contrib.auth` User, who should
                       receive the message, optionally multiple usernames
                       could be separated by a '+'
        ``form_class``: the form-class to use
        ``template_name``: the template to use
        ``success_url``: where to redirect after successfull submission
    """
    user = request.user

    searchForm = SearchForm(request.POST) # Cuadro de búsqueda
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial) # Mostrar formulario para enviar mensajes.

    user_profile = user
     # cargar lista de amigos (12 primeros)
    try:
        #friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends
    message_list = Message.objects.inbox_for(request.user)

    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=request.user)
            messages.info(request, _(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            if 'next' in request.GET:
                success_url = request.GET['next']
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
        if recipient is not None:
            recipients = [u for u in User.objects.filter(**{'%s__in' % get_username_field(): [r.strip() for r in recipient.split('+')]})]
            form.fields['recipient'].initial = recipients
    return render_to_response(template_name, {
        'form': form, 'friends_top12': friends_top12,
    'publicationSelfForm': publicationForm, 'searchForm': searchForm, 'message_list': message_list}, context_instance=RequestContext(request))

@login_required(login_url='/')
def compose_username(request, recipient=None, form_class=ComposeForm,
                     recipient_filter=None, template_name='django_messages/compose.html',
                     success_url=None):
    user = request.user

    searchForm = SearchForm(request.POST) # Cuadro de búsqueda
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial) # Mostrar formulario para enviar mensajes.

    user_profile = user
     # cargar lista de amigos (12 primeros)
    try:
        #friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends
        message_list = Message.objects.inbox_for(request.user)

        if request.method == "POST":
            sender = request.user
            form = form_class(request.POST, recipient_filter=recipient_filter)
            if form.is_valid():
                form.save(sender=request.user)
                messages.info(request, _(u"Message successfully sent."))
                if success_url is None:
                    success_url = reverse('messages_inbox')
                if 'next' in request.GET:
                    success_url = request.GET['next']
                return HttpResponseRedirect(success_url)
        else:
            form = form_class()
            if recipient is not None:
                form.fields['recipient'].initial = recipient
        return render_to_response(template_name, {
            'form': form, 'friends_top12': friends_top12,
            'publicationSelfForm': publicationForm, 'searchForm': searchForm, 'message_list': message_list},
                                  context_instance=RequestContext(request))

@login_required(login_url='/')
def reply(request,message_id, form_class=ComposeForm,
        template_name='django_messages/compose.html', success_url=None,
        recipient_filter=None, quote_helper=format_quote,
        subject_template=_(u"Re: %(subject)s"),):
    """
    Prepares the ``form_class`` form for writing a reply to a given message
    (specified via ``message_id``). Uses the ``format_quote`` helper from
    ``messages.utils`` to pre-format the quote. To change the quote format
    assign a different ``quote_helper`` kwarg in your url-conf.

    """
    user = request.user

    searchForm = SearchForm(request.POST) # Cuadro de búsqueda
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial) # Mostrar formulario para enviar mensajes.

    user_profile = user
     # cargar lista de amigos (12 primeros)
    try:
        #friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends
    message_list = Message.objects.inbox_for(request.user)

    parent = get_object_or_404(Message, id=message_id)

    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404

    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=request.user, parent_msg=parent)
            messages.info(request, _(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            return HttpResponseRedirect(success_url)
    else:
        parent.body = re.sub(r'<[^>]*>', r'', parent.body) # eliminamos html tags
        form = form_class(initial={
            # 'body': quote_helper(parent.sender, parent.body),
            'subject': subject_template % {'subject': parent.subject},
            'recipient': parent.sender.username, # [parent.sender ,]
            })
    return render_to_response(template_name, {
        'form': form, 'friends_top12': friends_top12,
    'searchForm': searchForm, 'publicationSelfForm': publicationForm,
    'parent_body': parent.body,
    'parent_username': parent.sender.username}, context_instance=RequestContext(request))

@login_required(login_url='/')
def delete(request, message_id, success_url=None):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.

    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """
    user = request.user
    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if success_url is None:
        success_url = reverse('messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
        messages.info(request, _(u"Message successfully deleted."))
        if notification:
            notification.send([user], "messages_deleted", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required(login_url='/')
def undelete(request, message_id, success_url=None):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    message = get_object_or_404(Message, id=message_id)
    undeleted = False
    if success_url is None:
        success_url = reverse('messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == user:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        messages.info(request, _(u"Message successfully recovered."))
        if notification:
            notification.send([user], "messages_recovered", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required(login_url='/')
def view(request,message_id, form_class=ComposeForm, quote_helper=format_quote,
        subject_template=_(u"Re: %(subject)s"),
        template_name='django_messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either
    the sender or the recipient. If the user is not allowed a 404
    is raised.
    If the user is the recipient and the message is unread
    ``read_at`` is set to the current datetime.
    If the user is the recipient a reply form will be added to the
    tenplate context, otherwise 'reply_form' will be None.
    """
    user = request.user

    searchForm = SearchForm(request.POST) # Cuadro de búsqueda
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial) # Mostrar formulario para enviar mensajes.

    user_profile = user
     # cargar lista de amigos (12 primeros)
    try:
        #friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]
        else:
            friends_top12 = friends

    # Django messages
    message_list = Message.objects.inbox_for(request.user)

    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        message.save()

    context = {'message': message, 'reply_form': None,
               'publicationSelfForm': publicationForm,
               'searchForm': searchForm}
    if message.recipient == user:
        form = form_class(initial={
            'body': quote_helper(message.sender, message.body),
            'subject': subject_template % {'subject': message.subject},
            'recipient': [message.sender,]
            })
        context['reply_form'] = form
    return render_to_response(template_name, context,
        context_instance=RequestContext(request))
