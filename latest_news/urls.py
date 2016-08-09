from django.conf.urls import url

from .views import news_and_updates

urlpatterns = [
    url(r'^inicio/mypublications/', 'latest_news.views.news_and_updates'),
]
