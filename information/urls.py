from django.conf.urls import url
from information.views import PolicyPrivacyView

app_name = "information"

urlpatterns = [url(r"^privacy/$", PolicyPrivacyView.as_view(), name="privacy")]
