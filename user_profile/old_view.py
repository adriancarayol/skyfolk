def profile_view(request, username,
        template="account/profile.html",
        extra_context=None):

    user = request.user
    # para mostarar el cuadro de busqueda en la pagina:
    searchForm = SearchForm(request.POST)

    # username es el nombre del perfil visitado, si coincide con user.username
    # entonces estamos ante el perfil del usuario logueado.
    user_profile = get_object_or_404(get_user_model(),
                                     username__iexact=username)

    # mostrar formulario para enviar comentarios/publicaciones
    initial = {'author': user.pk, 'board_owner': user_profile.pk}
    publicationForm = PublicationForm(initial=initial)
    reply_pub_form = ReplyPublicationForm(initial=initial)

    # Vamos a comprobar la visibilidad del perfil que visitamos
    privacity = user_profile.profile.is_visible(user.profile, user.pk)
    template = 'account/profile.html'

    if privacity == "all":
        template = 'account/profile.html'

    elif privacity == "nothing":
        template = 'account/privacity/private_profile.html'
        return render_to_response(template, {
            'user_profile': user_profile,
            'searchForm': searchForm,
            'privacity': privacity, },
            context_instance=RequestContext(request))

    elif privacity == "block":
        template = 'account/privacity/block_profile.html'
        return render_to_response(template, {
            'user_profile': user_profile,
            'searchForm': searchForm,
            'privacity': privacity, },
            context_instance=RequestContext(request))
    print('>>> Estado de la cuenta: ' + str(user.is_active))
    print('>>> Visibilidad: ' + str(privacity))

    json_requestsToMe = None
    # saber si el usuario que visita el perfil le gusta
    if request.user.username != username:
        liked = True
        try:
            '''LikeProfile.objects.get(from_like=request.user.profile.id,
            to_like=user_profile.profile)'''
            request.user.profile.has_like(user_profile.profile)
        except ObjectDoesNotExist:
            liked = False
    else:
        liked = False
        requestsToMe = user.profile.get_received_friends_requests()

        if requestsToMe:
            requestsToMe_result = list()
            for item in requestsToMe:
                print(item)
                print(str(item.pk) + " " +
                      item.user.username + " " +
                      item.user.email)
                requestsToMe_result.append(
                    {'id_profile': item.pk, 'username': item.user.username, })

            # print requestsToMe_result
            json_requestsToMe = json.dumps(requestsToMe_result)

    print('LIKED? ' + str(liked))

    # saber si sigo al perfil que visito
    if request.user.username != username:
        isFriend = False
        try:
            if request.user.profile.is_follow(user_profile.profile):
                isFriend = True
        except ObjectDoesNotExist:
            isFriend = False
    else:
        isFriend = False

    # saber si el perfil que visito me sigue

    if request.user.username != username:
        isFollower = False
        try:
            if request.user.profile.is_follower(user_profile.profile):
                isFollower = True
        except ObjectDoesNotExist:
            isFollower = False
    else:
        isFollower = False

    # saber si el perfil que visito esta bloqueado
    if request.user.username != username:
        isBlocked = False
        try:
            if request.user.profile.is_blocked(user_profile.profile):
                isBlocked = True
        except ObjectDoesNotExist:
            isBlocked = False
    else:
        isBlocked = False

    print('IS BLOCKED? ' + str(isBlocked))
    # number of likes to him
    n_likes = len(user_profile.profile.likesToMe.all())

    try:
        friend_request = user.profile.get_follow_request(user_profile.profile)
    except ObjectDoesNotExist:
        friend_request = None

    if friend_request:
        existFollowRequest = True
        print('Exist follow request? ' + str(True))
    else:
        existFollowRequest = False
        print('Exist follow request? ' + str(False))

    # cargar lista de amigos (12 primeros)
    try:
        # friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends is not None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends

    # obtener num de seguidores
    try:
        followers = user_profile.profile.get_followers().count()
    except ObjectDoesNotExist:
        followers = None
    # obtener num de seguidos
    try:
        following = user_profile.profile.get_following().count()
    except ObjectDoesNotExist:
        following = None

    multimedia_count = user_profile.profile.get_num_multimedia()

    if privacity == "followers":
        template = 'account/privacity/need_confirmation_profile.html'
        return render_to_response(template, {
            'friends_top12': friends_top12,
            'user_profile': user_profile,
            'searchForm': searchForm,
            'liked': liked, 'n_likes': n_likes,
            'existFollowRequest': existFollowRequest,
            'json_requestsToMe': json_requestsToMe,
            'followers': followers,
            'privacity': privacity,
            'isFollower': isFollower,
            'following': following,
            'isBlocked': isBlocked, 'multimedia_count': multimedia_count},
            context_instance=RequestContext(request))

    elif privacity == "both":
        template = 'account/privacity/need_confirmation_profile.html'
        return render_to_response(template, {
            'friends_top12': friends_top12,
            'user_profile': user_profile,
            'searchForm': searchForm,
            'liked': liked, 'n_likes': n_likes,
            'existFollowRequest': existFollowRequest,
            'json_requestsToMe': json_requestsToMe,
            'followers': followers,
            'privacity': privacity,
            'isFollower': isFollower,
            'following': following,
            'isBlocked': isBlocked, 'multimedia_count': multimedia_count},
            context_instance=RequestContext(request))

    # cargar lista comentarios
    try:
        # publications = Publication.objects.get_authors_publications(
        #                                             author_pk=user_profile.pk)
        if user_profile.username == username:
            publications = Publication.objects.get_friend_profile_publications(
                user_pk=user_profile.pk,
                board_owner_pk=user_profile.pk)
        else:
            publications = Publication.objects.get_user_profile_publications(
                user_pk=user.pk,
                board_owner_pk=user_profile.pk)
        print('>>>>>>> LISTA PUBLICACIONES: ')
        # print publications
        print(publications)
    except ObjectDoesNotExist:
        publications = None

    print('>>>>>>> LISTA PUBLICACIONES TOP 15: ')
    # print publications
    print(publications)

    # cargar timeline
    print('>>>>>>>>>>> TIMELINE <<<<<<<<<<<')
    print('views.py line:164 publications_top {}'.format(publications))
    try:
        timeline = user_profile.profile.getTimelineToMe()
    except ObjectDoesNotExist:
        timeline = None

    context = dict({
        'publications': publications,
        'friends_top12': friends_top12,
        'user_profile': user_profile,
        'searchForm': searchForm,
        'publicationForm': publicationForm,
        'reply_publication_form': reply_pub_form,
        'liked': liked, 'n_likes': n_likes,
        'timeline': timeline, 'isFriend': isFriend,
        'existFollowRequest': existFollowRequest,
        'json_requestsToMe': json_requestsToMe,
        'followers': followers,
        'privacity': privacity,
        'isFollower': isFollower,
        'following': following,
        'isBlocked': isBlocked,
        'multimedia_count': multimedia_count
        })

    if extra_context is not None:
        context.update(extra_context)

    return render_to_response(template, context, context_instance=RequestContext(request))


