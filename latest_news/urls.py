from django.conf.urls import url
from latest_news import views as latest_news_views

urlpatterns = [
    url(r'^inicio/$', latest_news_views.news_and_updates),
]
