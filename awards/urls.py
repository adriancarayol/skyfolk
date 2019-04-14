from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from awards import views

app_name = "awards"

urlpatterns = [
    url(
        r"^user/(?P<user_id>\d+)/$",
        login_required(views.UserAwards.as_view()),
        name="awards-user",
    )
]
