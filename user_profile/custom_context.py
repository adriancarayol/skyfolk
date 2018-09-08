from user_groups.forms import FormUserGroup
from user_profile.forms import SearchForm


def user_processor(request):
    user = request.user
    if not user:
        return {}
    if user and not user.is_authenticated():
        return {}

    total_notifications = user.notifications.unread().count()
    
    if total_notifications > 20:
        total_notifications = "+" + str(20)

    return {
            'user_notifications': user.notifications.unread_limit(),
            'total_notifications': total_notifications,
            'searchForm': SearchForm(),
            'groupForm': FormUserGroup(initial={'owner': user.pk})
            }
