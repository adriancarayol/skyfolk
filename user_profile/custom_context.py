from user_profile.forms import SearchForm

def notifications_processor(request):
    user = request.user
    if user and not user.is_authenticated():
        return {}
    return {'notifications': user.notifications.unread_limit()}

def search_processor(request):
    user = request.user
    if user and not user.is_authenticated():
        return {}
    return {'searchForm': SearchForm()}