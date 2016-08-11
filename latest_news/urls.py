from django.conf.urls import url

urlpatterns = [
    url(r'^inicio/$', 'latest_news.views.news_and_updates'),
]
