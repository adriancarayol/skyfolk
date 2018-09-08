from django.conf.urls import url
from feedback.views import FeedbackView, FeedbackSuccess

urlpatterns = [
    url(r'^contact$', FeedbackView.as_view(), name='feedback_contact'),
    url(r'^success', FeedbackSuccess.as_view(), name='feedback_success'),
]
