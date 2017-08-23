from user_profile.forms import SearchForm

from user_groups.forms import FormUserGroup


def user_processor(request):
    user = request.user
    if not user:
        return {}
    if user and not user.is_authenticated():
        return {}
    return {
            'user_notifications': user.notifications.unread_limit(),
            'searchForm': SearchForm(),
            'groupForm': FormUserGroup(initial={'owner': user.pk})
            }
