from user_profile.forms import SearchForm

from user_groups.forms import FormUserGroup

def notifications_processor(request):
    user = request.user
    if user and not user.is_authenticated():
        return {}
    return {'user_notifications': user.notifications.unread_limit()}


def search_processor(request):
    user = request.user
    if user and not user.is_authenticated():
        return {}
    return {'searchForm': SearchForm()}

def group_processor(request):
    user= request.user
    if user and not user.is_authenticated():
        return {}
    return {'groupForm': FormUserGroup(initial={'owner': user.pk})}
