from django.urls import path

from latest_news import views as latest_news_views

app_name = "latest_news"

urlpatterns = [
    path("salad/", latest_news_views.news_and_updates, name="user-feed"),
]
