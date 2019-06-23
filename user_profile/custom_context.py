from user_groups.forms import FormUserGroup
from user_profile.forms import SearchForm


def user_processor(request):
    user = request.user
    initial_context = {
        "searchForm": SearchForm(),
    }

    if not user:
        return {}

    if user and not user.is_authenticated:
        return initial_context

    total_notifications = user.notifications.unread().count()

    if total_notifications > 20:
        total_notifications = "+" + str(20)

    initial_context.update({
        "user_notifications": user.notifications.unread_limit(),
        "total_notifications": total_notifications,
        "groupForm": FormUserGroup(initial={"owner": user.pk}),
    })

    return initial_context
